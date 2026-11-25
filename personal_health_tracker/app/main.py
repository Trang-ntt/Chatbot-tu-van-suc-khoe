from datetime import datetime, timedelta, timezone
import os, io, csv
import bcrypt, jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from openpyxl import Workbook
from .db import connect, init_db
from .analytics import analyze_series

load_dotenv()
SECRET=os.getenv("JWT_SECRET","development-secret-change-this-to-32chars")
security=HTTPBearer()
app=FastAPI(title="Personal Health Tracker",description="Dữ liệu giả lập; không chẩn đoán.")
METRICS={"blood_pressure","weight","glucose","heart_rate","sleep"}

@app.on_event("startup")
def startup(): init_db()

def current_user(c:HTTPAuthorizationCredentials=Depends(security)):
    try: p=jwt.decode(c.credentials,SECRET,algorithms=["HS256"])
    except jwt.PyJWTError: raise HTTPException(401,"Token không hợp lệ.")
    with connect() as db: u=db.execute("SELECT id,username,role,active FROM users WHERE id=?",(p["sub"],)).fetchone()
    if not u or not u["active"]: raise HTTPException(401,"Tài khoản không hoạt động.")
    return dict(u)

def only_user(u=Depends(current_user)):
    if u["role"]!="user": raise HTTPException(403,"Chức năng dành cho người dùng.")
    return u

class Credentials(BaseModel):
    username:str=Field(min_length=3,max_length=40)
    password:str=Field(min_length=8,max_length=100)
class Profile(BaseModel):
    full_name:str=""
    birth_date:str=""
    sex:str=""
    height_cm:float|None=None
    medical_history:str=""
    health_goals:str=""
class Measurement(BaseModel):
    metric:str
    value:float
    secondary_value:float|None=None
    unit:str
    measured_at:str
    note:str=""
class Limit(BaseModel):
    metric:str
    min_value:float|None=None
    max_value:float|None=None
    sudden_change_pct:float=20
    source_name:str
    source_url:str
    context:str=""
class Reminder(BaseModel):
    reminder_type:str
    title:str
    due_at:str
    repeat_rule:str="none"
class ShareRequest(BaseModel):
    viewer_username:str
    scope:str="metrics"
    consent:bool=False

@app.get("/api/health")
def health(): return {"status":"ok","database":"SQLite","demo_data_only":True}

@app.post("/api/auth/register")
def register(x:Credentials):
    with connect() as db:
        if db.execute("SELECT id FROM users WHERE username=?",(x.username,)).fetchone(): raise HTTPException(409,"Tên đăng nhập đã tồn tại.")
        cur=db.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",(x.username,bcrypt.hashpw(x.password.encode(),bcrypt.gensalt()).decode(),"user"))
        db.execute("INSERT INTO profiles(user_id) VALUES(?)",(cur.lastrowid,))
    return {"message":"Đăng ký thành công."}

@app.post("/api/auth/login")
def login(x:Credentials):
    with connect() as db: u=db.execute("SELECT * FROM users WHERE username=? AND active=1",(x.username,)).fetchone()
    if not u or not bcrypt.checkpw(x.password.encode(),u["password_hash"].encode()): raise HTTPException(401,"Sai tài khoản hoặc mật khẩu.")
    token=jwt.encode({"sub":str(u["id"]),"exp":datetime.now(timezone.utc)+timedelta(hours=12)},SECRET,algorithm="HS256")
    return {"access_token":token,"token_type":"bearer","role":u["role"],"username":u["username"]}

@app.get("/api/me")
def me(u=Depends(current_user)): return {k:u[k] for k in ("id","username","role")}

@app.get("/api/admin/users")
def users(u=Depends(current_user)):
    if u["role"]!="admin": raise HTTPException(403,"Chỉ admin.")
    with connect() as db: return [dict(r) for r in db.execute("SELECT id,username,role,active FROM users").fetchall()]

@app.get("/api/profile")
def get_profile(u=Depends(only_user)):
    with connect() as db: r=db.execute("SELECT * FROM profiles WHERE user_id=?",(u["id"],)).fetchone()
    return dict(r) if r else {}

@app.put("/api/profile")
def put_profile(x:Profile,u=Depends(only_user)):
    with connect() as db:
        db.execute("""INSERT INTO profiles VALUES(?,?,?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET
        full_name=excluded.full_name,birth_date=excluded.birth_date,sex=excluded.sex,height_cm=excluded.height_cm,
        medical_history=excluded.medical_history,health_goals=excluded.health_goals""",
        (u["id"],x.full_name,x.birth_date,x.sex,x.height_cm,x.medical_history,x.health_goals))
    return {"message":"Đã lưu hồ sơ."}

@app.get("/api/metrics")
def metrics(metric:str|None=None,u=Depends(only_user)):
    with connect() as db:
        sql="SELECT * FROM metrics WHERE user_id=?"; args=[u["id"]]
        if metric:
            if metric not in METRICS: raise HTTPException(400,"Loại chỉ số không hợp lệ.")
            sql+=" AND metric=?";args.append(metric)
        return [dict(r) for r in db.execute(sql+" ORDER BY measured_at DESC",args).fetchall()]

@app.post("/api/metrics")
def add_metric(x:Measurement,u=Depends(only_user)):
    if x.metric not in METRICS: raise HTTPException(400,"Loại chỉ số không hợp lệ.")
    try: datetime.fromisoformat(x.measured_at.replace("Z","+00:00"))
    except ValueError: raise HTTPException(400,"Thời điểm phải ở dạng ISO.")
    if x.metric=="blood_pressure" and x.secondary_value is None: raise HTTPException(400,"Huyết áp cần tâm thu và tâm trương.")
    with connect() as db:
        cur=db.execute("INSERT INTO metrics(user_id,metric,value,secondary_value,unit,measured_at,note) VALUES(?,?,?,?,?,?,?)",(u["id"],x.metric,x.value,x.secondary_value,x.unit,x.measured_at,x.note))
        m=db.execute("SELECT * FROM thresholds WHERE user_id=? AND metric=?",(u["id"],x.metric)).fetchone()
        if m and x.metric!="blood_pressure" and ((m["min_value"] is not None and x.value<m["min_value"]) or (m["max_value"] is not None and x.value>m["max_value"])):
            db.execute("INSERT INTO alerts(user_id,metric,metric_id,alert_type,message,severity) VALUES(?,?,?,?,?,?)",(u["id"],x.metric,cur.lastrowid,"threshold","Giá trị vượt ngưỡng bạn đã cài đặt. Kiểm tra lại phép đo và hỏi nhân viên y tế nếu lo ngại.","warning"))
        prev=db.execute("SELECT value FROM metrics WHERE user_id=? AND metric=? AND id<>? ORDER BY measured_at DESC LIMIT 1",(u["id"],x.metric,cur.lastrowid)).fetchone()
        if prev and prev["value"] and abs(x.value-prev["value"])/abs(prev["value"])*100 >= (m["sudden_change_pct"] if m else 20):
            db.execute("INSERT INTO alerts(user_id,metric,metric_id,alert_type,message,severity) VALUES(?,?,?,?,?,?)",(u["id"],x.metric,cur.lastrowid,"change","Chỉ số thay đổi đột ngột so với lần đo trước; hãy đo lại và theo dõi.","warning"))
    return {"id":cur.lastrowid,"message":"Đã lưu."}

@app.delete("/api/metrics/{mid}")
def delete_metric(mid:int,u=Depends(only_user)):
    with connect() as db:
        c=db.execute("DELETE FROM metrics WHERE id=? AND user_id=?",(mid,u["id"]))
        if not c.rowcount: raise HTTPException(404,"Không tìm thấy.")
    return {"message":"Đã xóa."}

@app.post("/api/metrics/import-csv")
async def import_csv(file:UploadFile=File(...),u=Depends(only_user)):
    if not file.filename.lower().endswith(".csv"): raise HTTPException(400,"Chỉ nhận CSV.")
    raw=await file.read()
    if len(raw)>2_000_000: raise HTTPException(413,"File quá lớn.")
    try: rows=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    except Exception: raise HTTPException(400,"CSV không hợp lệ.")
    count=0
    with connect() as db:
        for r in rows:
            try:
                if r["metric"] not in METRICS: continue
                datetime.fromisoformat(r["measured_at"].replace("Z","+00:00"))
                v=float(r["value"]); sv=float(r["secondary_value"]) if r.get("secondary_value") else None
                if r["metric"]=="blood_pressure" and sv is None: continue
                db.execute("INSERT INTO metrics(user_id,metric,value,secondary_value,unit,measured_at,note) VALUES(?,?,?,?,?,?,?)",(u["id"],r["metric"],v,sv,r.get("unit",""),r["measured_at"],r.get("note","CSV")))
                count+=1
            except (ValueError,KeyError): continue
    return {"inserted":count}

@app.post("/api/thresholds")
def set_limit(x:Limit,u=Depends(only_user)):
    if x.metric not in METRICS or (x.min_value is None and x.max_value is None): raise HTTPException(400,"Ngưỡng không hợp lệ.")
    if x.min_value is not None and x.max_value is not None and x.min_value>=x.max_value: raise HTTPException(400,"Ngưỡng dưới phải nhỏ hơn ngưỡng trên.")
    with connect() as db:
        db.execute("""INSERT INTO thresholds(user_id,metric,min_value,max_value,sudden_change_pct,source_name,source_url,context)
        VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(user_id,metric) DO UPDATE SET min_value=excluded.min_value,max_value=excluded.max_value,
        sudden_change_pct=excluded.sudden_change_pct,source_name=excluded.source_name,source_url=excluded.source_url,context=excluded.context""",
        (u["id"],x.metric,x.min_value,x.max_value,x.sudden_change_pct,x.source_name,x.source_url,x.context))
    return {"message":"Đã lưu ngưỡng và nguồn."}

@app.get("/api/thresholds")
def limits(u=Depends(only_user)):
    with connect() as db: return [dict(r) for r in db.execute("SELECT * FROM thresholds WHERE user_id=?",(u["id"],)).fetchall()]

@app.get("/api/alerts")
def alerts(u=Depends(only_user)):
    with connect() as db: return [dict(r) for r in db.execute("SELECT * FROM alerts WHERE user_id=? ORDER BY created_at DESC",(u["id"],)).fetchall()]

@app.get("/api/analytics/trends")
def trends(metric:str,period:str="month",u=Depends(only_user)):
    if metric not in METRICS or period not in {"week","month","all"}: raise HTTPException(400,"Tham số không hợp lệ.")
    cutoff={"week":"-7 days","month":"-30 days"}.get(period)
    with connect() as db:
        sql="SELECT value,secondary_value,unit,measured_at FROM metrics WHERE user_id=? AND metric=?";args=[u["id"],metric]
        if cutoff: sql+=" AND measured_at>=datetime('now',?)";args.append(cutoff)
        rows=[dict(r) for r in db.execute(sql+" ORDER BY measured_at",args).fetchall()]
    result=analyze_series([r["value"] for r in rows])
    if metric=="blood_pressure": result["diastolic"]=analyze_series([r["secondary_value"] for r in rows if r["secondary_value"] is not None])
    return {"metric":metric,"records":rows,"analysis":result}

@app.post("/api/reminders")
def add_reminder(x:Reminder,u=Depends(only_user)):
    if x.reminder_type not in {"measure","medicine","exercise","other"}: raise HTTPException(400,"Loại nhắc không hợp lệ.")
    with connect() as db: c=db.execute("INSERT INTO reminders(user_id,reminder_type,title,due_at,repeat_rule) VALUES(?,?,?,?,?)",(u["id"],x.reminder_type,x.title,x.due_at,x.repeat_rule))
    return {"id":c.lastrowid}

@app.get("/api/reminders")
def reminders(u=Depends(only_user)):
    with connect() as db: return [dict(r) for r in db.execute("SELECT * FROM reminders WHERE user_id=? AND active=1 ORDER BY due_at",(u["id"],)).fetchall()]

@app.delete("/api/reminders/{rid}")
def remove_reminder(rid:int,u=Depends(only_user)):
    with connect() as db: c=db.execute("UPDATE reminders SET active=0 WHERE id=? AND user_id=?",(rid,u["id"]))
    if not c.rowcount: raise HTTPException(404,"Không tìm thấy.")
    return {"message":"Đã tắt."}

@app.post("/api/shares")
def share(x:ShareRequest,u=Depends(only_user)):
    if not x.consent: raise HTTPException(400,"Bạn phải xác nhận đồng ý.")
    with connect() as db:
        v=db.execute("SELECT id,role FROM users WHERE username=? AND active=1",(x.viewer_username,)).fetchone()
        if not v or v["role"]!="viewer": raise HTTPException(404,"Không tìm thấy tài khoản viewer.")
        db.execute("INSERT INTO shares(owner_id,viewer_id,scope,revoked_at) VALUES(?,?,?,NULL) ON CONFLICT(owner_id,viewer_id,scope) DO UPDATE SET consented_at=CURRENT_TIMESTAMP,revoked_at=NULL",(u["id"],v["id"],x.scope))
    return {"message":"Đã chia sẻ theo sự đồng ý."}

@app.get("/api/shares")
def shares(u=Depends(only_user)):
    with connect() as db: return [dict(r) for r in db.execute("SELECT s.*,v.username viewer_username FROM shares s JOIN users v ON v.id=s.viewer_id WHERE owner_id=?",(u["id"],)).fetchall()]

@app.delete("/api/shares/{sid}")
def revoke(sid:int,u=Depends(only_user)):
    with connect() as db: c=db.execute("UPDATE shares SET revoked_at=CURRENT_TIMESTAMP WHERE id=? AND owner_id=? AND revoked_at IS NULL",(sid,u["id"]))
    if not c.rowcount: raise HTTPException(404,"Không có quyền chia sẻ.")
    return {"message":"Đã thu hồi."}

@app.get("/api/shared/{owner_id}/metrics")
def shared_metrics(owner_id:int,u=Depends(current_user)):
    if u["role"]!="viewer": raise HTTPException(403,"Chỉ viewer.")
    with connect() as db:
        s=db.execute("SELECT id FROM shares WHERE owner_id=? AND viewer_id=? AND revoked_at IS NULL",(owner_id,u["id"])).fetchone()
        if not s: raise HTTPException(403,"Chưa được chủ tài khoản cho phép.")
        return [dict(r) for r in db.execute("SELECT metric,value,secondary_value,unit,measured_at FROM metrics WHERE user_id=? ORDER BY measured_at DESC",(owner_id,)).fetchall()]

@app.get("/api/reports/export.xlsx")
def export_xlsx(u=Depends(only_user)):
    with connect() as db: rows=db.execute("SELECT metric,value,secondary_value,unit,measured_at,note FROM metrics WHERE user_id=? ORDER BY measured_at",(u["id"],)).fetchall()
    w=Workbook();s=w.active;s.append(["Chỉ số","Giá trị","Giá trị phụ","Đơn vị","Thời điểm","Ghi chú"])
    for r in rows:s.append(list(r))
    b=io.BytesIO();w.save(b);b.seek(0)
    return StreamingResponse(b,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":"attachment; filename=health_report.xlsx"})

@app.get("/")
def home():
    from fastapi.responses import HTMLResponse
    return HTMLResponse("<h1>Personal Health Tracker API</h1><p>Open <a href='/docs'>/docs</a> to use the application API.</p>")
