import os
import requests

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth import current_user
from database import query, execute


router = APIRouter(
    prefix="/api/chat",
    tags=["Chatbot"]
)


# ============================================================
# CẤU HÌNH RASA
# ============================================================

RASA_URL = os.getenv(
    "RASA_REST_URL",
    "http://localhost:5005/webhooks/rest/webhook"
)


# ============================================================
# MODEL
# ============================================================

class ChatIn(BaseModel):
    message: str


# ============================================================
# FALLBACK
# ============================================================

def fallback(message: str) -> str:

    m = message.lower()

    if any(x in m for x in ["xin chào", "chào", "hello", "hi"]):
        return (
            "Xin chào! Tôi là Chatbot Y tế. "
            "Bạn muốn hỏi về sức khỏe hay triệu chứng?"
        )

    if "tái khám" in m:
        return (
            "Bạn có thể mở mục "
            "Lịch tái khám để xem các lịch hẹn của mình."
        )

    if "thuốc" in m or "uống thuốc" in m:
        return (
            "Bạn có thể mở mục "
            "Nhắc uống thuốc để thêm và theo dõi lịch uống thuốc."
        )

    return (
        "Tôi đã ghi nhận câu hỏi. "
        "Nếu Rasa đang chạy, hệ thống sẽ chuyển câu hỏi "
        "sang mô hình Rasa để trả lời."
    )


# ============================================================
# CHAT
# ============================================================

@router.post("")
def chat(
    data: ChatIn,
    user=Depends(current_user)
):

    message = data.message.strip()

    if not message:
        return {
            "reply": "Bạn hãy nhập nội dung cần hỏi."
        }

    # UserId lấy từ SQLite
    user_id = user["UserId"]

    reply = None

    # ========================================================
    # GỌI RASA
    # ========================================================

    try:

        response = requests.post(
            RASA_URL,
            json={
                "sender": str(user_id),
                "message": message
            },
            timeout=10
        )

        if response.ok:

            rasa_data = response.json()

            if rasa_data:

                replies = []

                for item in rasa_data:

                    text = item.get("text")

                    if text:
                        replies.append(text)

                if replies:
                    reply = "\n".join(replies)

    except requests.RequestException as e:

        print("Không kết nối được Rasa:", e)

    # ========================================================
    # FALLBACK
    # ========================================================

    if not reply:
        reply = fallback(message)

    # ========================================================
    # LƯU LỊCH SỬ CHAT
    # ========================================================

    try:

        execute(
            """
            INSERT INTO ChatHistory
            (
                UserID,
                Message,
                Response,
                CreatedAt
            )
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                user_id,
                message,
                reply
            )
        )

    except Exception as e:

        print("Không thể lưu lịch sử chatbot:", e)

    # ========================================================
    # TRẢ KẾT QUẢ
    # ========================================================

    return {
        "message": message,
        "reply": reply
    }


# ============================================================
# LỊCH SỬ CHAT CỦA USER
# ============================================================

@router.get("/mine")
def my_chat_history(
    user=Depends(current_user)
):

    user_id = user["UserId"]

    try:

        return query(
            """
            SELECT
                ID,
                Message,
                Response,
                CreatedAt
            FROM ChatHistory
            WHERE UserID = ?
            ORDER BY CreatedAt DESC
            """,
            (user_id,)
        )

    except Exception as e:

        print("Không thể lấy lịch sử chatbot:", e)

        return []