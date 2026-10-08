from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import bcrypt

from database import query, execute
from auth import make_token, public_user, current_user


router = APIRouter(
    prefix="/api",
    tags=["Auth"]
)


# ============================================================
# MODEL
# ============================================================

class RegisterBody(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginBody(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# ĐĂNG KÝ
# ============================================================

@router.post("/register")
def register(b: RegisterBody):

    # Kiểm tra email đã tồn tại chưa
    existing = query(
        """
        SELECT UserId
        FROM Users
        WHERE Email = ?
        """,
        (str(b.email),),
        one=True
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email đã được đăng ký"
        )

    # Dùng email làm Username
    username = str(b.email)

    # Mã hóa mật khẩu bằng bcrypt
    hashed = bcrypt.hashpw(
        b.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:
        user_id = execute(
            """
            INSERT INTO Users
            (
                Username,
                PasswordHash,
                FullName,
                Email,
                Role,
                IsActive
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                hashed,
                b.full_name.strip(),
                str(b.email),
                "user",
                1
            )
        )

    except Exception as e:
        print("Lỗi đăng ký:", e)

        raise HTTPException(
            status_code=500,
            detail="Không thể tạo tài khoản"
        )

    return {
        "message": "Đăng ký thành công",
        "UserId": user_id
    }


# ============================================================
# ĐĂNG NHẬP
# ============================================================

@router.post("/login")
def login(b: LoginBody):

    user = query(
        """
        SELECT *
        FROM Users
        WHERE Email = ?
        """,
        (str(b.email),),
        one=True
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không đúng"
        )

    # Kiểm tra tài khoản có bị khóa không
    if not user.get("IsActive", 1):
        raise HTTPException(
            status_code=403,
            detail="Tài khoản đã bị khóa"
        )

    # Kiểm tra mật khẩu
    try:
        password_hash = user.get("PasswordHash")

        if not password_hash:
            password_correct = False
        else:
            password_correct = bcrypt.checkpw(
                b.password.encode("utf-8"),
                password_hash.encode("utf-8")
            )

    except Exception as e:
        print("Lỗi kiểm tra mật khẩu:", e)
        password_correct = False

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không đúng"
        )

    # Tạo JWT
    token = make_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": public_user(user)
    }


# ============================================================
# THÔNG TIN USER HIỆN TẠI
# ============================================================

@router.get("/me")
def get_me(user=Depends(current_user)):
    return public_user(user)