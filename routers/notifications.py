from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import current_user
from database import query, execute


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


# =========================
# DỮ LIỆU TẠO THÔNG BÁO
# =========================

class NotificationIn(BaseModel):
    title: str
    message: str


# =========================
# 1. XEM THÔNG BÁO CỦA MÌNH
# =========================

@router.get("/mine")
def get_my_notifications(
    user=Depends(current_user)
):
    notifications = query(
        """
        SELECT
            NotificationId,
            Title,
            Message,
            NotificationType,
            SentAt,
            Status
        FROM Notifications
        WHERE UserId = ?
        ORDER BY SentAt DESC
        """,
        (user["UserId"],)
    )

    return notifications


# =========================
# 2. TẠO THÔNG BÁO
# =========================

@router.post("")
def create_notification(
    data: NotificationIn,
    user=Depends(current_user)
):
    notification_id = execute(
        """
        INSERT INTO Notifications
        (
            UserId,
            Title,
            Message,
            NotificationType,
            Status
        )
        VALUES (?, ?, ?, 'web', 'unread')
        """,
        (
            user["UserId"],
            data.title,
            data.message
        )
    )

    return {
        "success": True,
        "message": "Đã tạo thông báo",
        "notification_id": notification_id
    }


# =========================
# 3. ĐÁNH DẤU MỘT THÔNG BÁO ĐÃ ĐỌC
# =========================

@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    user=Depends(current_user)
):
    notification = query(
        """
        SELECT NotificationId
        FROM Notifications
        WHERE NotificationId = ?
          AND UserId = ?
        """,
        (
            notification_id,
            user["UserId"]
        ),
        one=True
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thông báo"
        )

    execute(
        """
        UPDATE Notifications
        SET Status = 'read'
        WHERE NotificationId = ?
          AND UserId = ?
        """,
        (
            notification_id,
            user["UserId"]
        )
    )

    return {
        "success": True,
        "message": "Đã đánh dấu thông báo đã đọc"
    }


# =========================
# 4. ĐÁNH DẤU TẤT CẢ ĐÃ ĐỌC
# =========================

@router.patch("/read-all")
def mark_all_as_read(
    user=Depends(current_user)
):
    execute(
        """
        UPDATE Notifications
        SET Status = 'read'
        WHERE UserId = ?
          AND Status = 'unread'
        """,
        (user["UserId"],)
    )

    return {
        "success": True,
        "message": "Đã đánh dấu tất cả thông báo là đã đọc"
    }