"""API Đăng ký / Đăng nhập / Quản trị người dùng.
Chạy: uvicorn main:app --reload      Mở: http://localhost:8000
"""
import os, datetime as dt
import bcrypt, jwt, pyodbc, smtplib
from email.message import EmailMessage
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field

# ---- Cấu hình (sửa theo máy bạn) ----
DB = r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=HealthBot;Trusted_Connection=yes;TrustServerCertificate=yes;"
JWT_SECRET = os.getenv("JWT_SECRET", "doi-chuoi-bi-mat-nay")
# ---- Gửi email đặt lại mật khẩu (tùy chọn). Không cấu hình thì link in ra Terminal ----
BASE_URL  = os.getenv("BASE_URL", "http://localhost:8000")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")     # vd: tai_khoan_gui@gmail.com
SMTP_PASS = os.getenv("SMTP_PASS")     # mật khẩu ứng dụng (App Password)

app = FastAPI(title="HealthBot Auth & Admin")

def _q(sql, params=(), fetch="all"):
    with pyodbc.connect(DB) as c:
        cur = c.cursor(); cur.execute(sql, params)
        if fetch is None:
            c.commit(); return None
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        return rows[0] if (fetch == "one" and rows) else (None if fetch == "one" else rows)

def q(*a, **k):
    try:
        return _q(*a, **k)
    except pyodbc.Error as e:
        raise HTTPException(500, "Lỗi cơ sở dữ liệu: " + str(e))

def make_token(u):
    exp = dt.datetime.utcnow() + dt.timedelta(hours=8)
    return jwt.encode({"sub": str(u["UserId"]), "role": u["Role"], "exp": exp}, JWT_SECRET, "HS256")

def current_user(authorization: str = Header(None)):
    try:
        data = jwt.decode((authorization or "").replace("Bearer ", ""), JWT_SECRET, ["HS256"])
    except Exception:
        raise HTTPException(401, "Phiên đăng nhập hết hạn, hãy đăng nhập lại")
    u = q("SELECT * FROM Users WHERE UserId=?", (data["sub"],), "one")
    if not u or not u["IsActive"]:
        raise HTTPException(403, "Tài khoản không tồn tại hoặc đã bị khóa")
    return u

def admin_only(u=Depends(current_user)):
    if u["Role"] != "admin":
        raise HTTPException(403, "Chỉ quản trị viên được truy cập")
    return u

def public(u):
    return {k: u[k] for k in ("UserId", "FullName", "Email", "Role")}

# ---- Đăng ký / Đăng nhập ----
class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=6)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@app.post("/api/register")
def register(b: RegisterIn):
    if q("SELECT 1 AS x FROM Users WHERE Email=?", (b.email,), "one"):
        raise HTTPException(409, "Email này đã được đăng ký")
    h = bcrypt.hashpw(b.password.encode(), bcrypt.gensalt()).decode()
    q("INSERT INTO Users(FullName,Email,PasswordHash) VALUES(?,?,?)", (b.full_name, b.email, h), None)
    return {"message": "Đăng ký thành công, hãy đăng nhập"}

@app.post("/api/login")
def login(b: LoginIn):
    u = q("SELECT * FROM Users WHERE Email=?", (b.email,), "one")
    if not u or not u["PasswordHash"] or not bcrypt.checkpw(b.password.encode(), u["PasswordHash"].encode()):
        raise HTTPException(401, "Email hoặc mật khẩu không đúng")
    if not u["IsActive"]:
        raise HTTPException(403, "Tài khoản đã bị khóa")
    q("UPDATE Users SET LastLoginAt=SYSDATETIME() WHERE UserId=?", (u["UserId"],), None)
    return {"token": make_token(u), "user": public(u)}

# ---- Đổi mật khẩu / Quên mật khẩu ----
class ChangePwIn(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)

class ForgotIn(BaseModel):
    email: EmailStr

class ResetIn(BaseModel):
    token: str
    new_password: str = Field(min_length=6)

def hash_pw(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

@app.post("/api/change-password")
def change_password(b: ChangePwIn, u=Depends(current_user)):
    if not u["PasswordHash"] or not bcrypt.checkpw(b.old_password.encode(), u["PasswordHash"].encode()):
        raise HTTPException(400, "Mật khẩu hiện tại không đúng")
    q("UPDATE Users SET PasswordHash=? WHERE UserId=?", (hash_pw(b.new_password), u["UserId"]), None)
    return {"message": "Đổi mật khẩu thành công"}

@app.post("/api/forgot-password")
def forgot_password(b: ForgotIn):
    u = q("SELECT * FROM Users WHERE Email=?", (b.email,), "one")
    if u and u["IsActive"]:
        # Token sống 15 phút, gắn với mật khẩu hiện tại nên chỉ dùng được 1 lần
        exp = dt.datetime.utcnow() + dt.timedelta(minutes=15)
        token = jwt.encode({"sub": str(u["UserId"]), "purpose": "reset",
                            "ph": (u["PasswordHash"] or "")[-10:], "exp": exp}, JWT_SECRET, "HS256")
        link = f"{BASE_URL}/?reset={token}"
        if SMTP_USER and SMTP_PASS:
            try:
                m = EmailMessage()
                m["Subject"], m["From"], m["To"] = "Đặt lại mật khẩu HealthBot", SMTP_USER, b.email
                m.set_content(f"Xin chào {u['FullName']},\n\nBấm vào liên kết sau để đặt lại mật khẩu "
                              f"(có hiệu lực 15 phút):\n{link}\n\nNếu không phải bạn yêu cầu, hãy bỏ qua email này.")
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as sv:
                    sv.starttls(); sv.login(SMTP_USER, SMTP_PASS); sv.send_message(m)
            except Exception as e:
                print("Lỗi gửi email:", e)
        else:
            print("\n[CHẾ ĐỘ DEMO] Liên kết đặt lại mật khẩu cho", b.email, ":\n", link, "\n")
    # Luôn trả lời giống nhau để không lộ email nào đã đăng ký
    return {"message": "Nếu email tồn tại, liên kết đặt lại mật khẩu đã được gửi. Liên kết có hiệu lực 15 phút."}

@app.post("/api/reset-password")
def reset_password(b: ResetIn):
    try:
        d = jwt.decode(b.token, JWT_SECRET, ["HS256"])
        assert d.get("purpose") == "reset"
    except Exception:
        raise HTTPException(400, "Liên kết không hợp lệ hoặc đã hết hạn")
    u = q("SELECT * FROM Users WHERE UserId=?", (d["sub"],), "one")
    if not u or (u["PasswordHash"] or "")[-10:] != d["ph"]:
        raise HTTPException(400, "Liên kết đã được sử dụng hoặc không còn hiệu lực")
    q("UPDATE Users SET PasswordHash=? WHERE UserId=?", (hash_pw(b.new_password), u["UserId"]), None)
    return {"message": "Đặt lại mật khẩu thành công, hãy đăng nhập"}

@app.get("/api/me")
def me(u=Depends(current_user)):
    return public(u)

# ---- Quản trị viên ----
@app.get("/api/admin/stats")
def stats(_=Depends(admin_only)):
    return q("""SELECT COUNT(*) AS total,
                SUM(CASE WHEN IsActive=1 THEN 1 ELSE 0 END) AS active,
                SUM(CASE WHEN Role='admin' THEN 1 ELSE 0 END) AS admins FROM Users""", fetch="one")

@app.get("/api/admin/conversations")
def conversations(_=Depends(admin_only)):
    return q("""SELECT TOP 200 c.ConvId, u.FullName, c.Sender, c.Message, c.CreatedAt
                FROM Conversations c JOIN Users u ON u.UserId=c.UserId ORDER BY c.CreatedAt DESC""")

@app.get("/api/admin/medications")
def medications(_=Depends(admin_only)):
    return q("""SELECT m.MedId, u.FullName, m.DrugName, m.Dosage, m.TimesPerDay, m.StartDate, m.EndDate, m.IsActive
                FROM Medications m JOIN Users u ON u.UserId=m.UserId ORDER BY m.StartDate DESC""")

@app.get("/api/admin/symptom-checks")
def symptom_checks(_=Depends(admin_only)):
    return q("""SELECT TOP 200 s.CheckId, u.FullName, s.SymptomText, s.Severity, s.DaysSince, s.CreatedAt
                FROM SymptomChecks s JOIN Users u ON u.UserId=s.UserId ORDER BY s.CreatedAt DESC""")

@app.get("/api/admin/appointments")
def appointments(_=Depends(admin_only)):
    return q("""SELECT a.ApptId, u.FullName, a.DoctorName, a.Location, a.ApptTime, a.Status, a.Channel
                FROM Appointments a JOIN Users u ON u.UserId=a.UserId ORDER BY a.ApptTime DESC""")

@app.get("/api/admin/users")
def list_users(search: str = "", _=Depends(admin_only)):
    like = f"%{search}%"
    return q("""SELECT UserId,FullName,Email,Role,IsActive,CreatedAt,LastLoginAt FROM Users
                WHERE FullName LIKE ? OR Email LIKE ? ORDER BY CreatedAt DESC""", (like, like))

class UserPatch(BaseModel):
    role: str | None = None
    is_active: bool | None = None

@app.patch("/api/admin/users/{uid}")
def patch_user(uid: int, b: UserPatch, a=Depends(admin_only)):
    if uid == a["UserId"]:
        raise HTTPException(400, "Không thể tự đổi quyền hoặc khóa chính mình")
    if b.role in ("user", "admin"):
        q("UPDATE Users SET Role=? WHERE UserId=?", (b.role, uid), None)
    if b.is_active is not None:
        q("UPDATE Users SET IsActive=? WHERE UserId=?", (int(b.is_active), uid), None)
    return {"message": "Đã cập nhật"}

@app.delete("/api/admin/users/{uid}")
def delete_user(uid: int, a=Depends(admin_only)):
    if uid == a["UserId"]:
        raise HTTPException(400, "Không thể xóa chính mình")
    q("DELETE FROM Users WHERE UserId=?", (uid,), None)
    return {"message": "Đã xóa"}

@app.get("/")
def index():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")