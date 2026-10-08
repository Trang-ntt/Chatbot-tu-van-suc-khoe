import os
import datetime as dt
import jwt

from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import query


JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "change-this-secret-key-to-at-least-32-chars"
)

JWT_ALGORITHM = "HS256"

# Tạo cơ chế Bearer Token cho Swagger
bearer_scheme = HTTPBearer(auto_error=False)


def make_token(user):
    exp = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=8)

    payload = {
        "sub": str(user["UserId"]),
        "role": user["Role"],
        "exp": exp
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def public_user(user):
    return {
        "UserId": user["UserId"],
        "FullName": user["FullName"],
        "Email": user["Email"],
        "Role": user["Role"]
    }


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme)
):
    # Không có token
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Vui lòng đăng nhập"
        )

    # Lấy JWT
    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token đăng nhập không hợp lệ"
        )

    # Giải mã JWT
    try:
        data = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Phiên đăng nhập đã hết hạn, hãy đăng nhập lại"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token đăng nhập không hợp lệ"
        )

    # Lấy UserId
    user_id = data.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token không chứa UserId"
        )

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="UserId trong token không hợp lệ"
        )

    # Kiểm tra User trong database
    try:
        user = query(
            "SELECT * FROM Users WHERE UserId = ?",
            (user_id,),
            one=True
        )

    except Exception as e:
        print("Lỗi truy vấn Users:", e)

        raise HTTPException(
            status_code=500,
            detail="Không thể truy cập cơ sở dữ liệu"
        )

    if not user:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản không tồn tại hoặc đã bị khóa"
        )

    # Kiểm tra tài khoản
    is_active = user.get("IsActive", 1)

    if not is_active:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản đã bị khóa"
        )

    return user