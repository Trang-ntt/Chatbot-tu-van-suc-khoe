from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import current_user
from database import query, execute


router = APIRouter(
    prefix="/api/appointments",
    tags=["Appointments"]
)


# ============================================================
# MODEL
# ============================================================

class AppointmentIn(BaseModel):
    doctor_name: str = Field(
        ...,
        min_length=1
    )

    location: str | None = None

    appt_time: datetime

    content: str | None = None

    note: str | None = None

    remind_before: int = Field(
        default=1440,
        ge=0
    )

    # Chỉ nhắc trong website
    channel: str = "web"


class AppointmentStatusBody(BaseModel):
    status: str


# ============================================================
# HÀM KIỂM TRA LỊCH THUỘC USER
# ============================================================

def get_user_appointment(
    appt_id: int,
    user_id: int
):

    appointment = query(
        """
        SELECT
            ApptId,
            UserId,
            DoctorName,
            Location,
            ApptTime,
            Content,
            Note,
            Status,
            RemindBefore,
            Channel,
            ConfirmedAt,
            ReminderCount,
            CreatedAt
        FROM Appointments
        WHERE ApptId = ?
          AND UserId = ?
        """,
        (
            appt_id,
            user_id
        ),
        one=True
    )

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy lịch tái khám"
        )

    return appointment


# ============================================================
# THÊM LỊCH TÁI KHÁM
# ============================================================

@router.post("")
def create_appointment(
    body: AppointmentIn,
    user=Depends(current_user)
):

    # --------------------------------------------------------
    # Kiểm tra thời gian
    # --------------------------------------------------------

    if body.appt_time is None:

        raise HTTPException(
            status_code=400,
            detail="Vui lòng chọn thời gian tái khám"
        )

    # --------------------------------------------------------
    # Chỉ cho phép nhắc trên website
    # --------------------------------------------------------

    channel = "web"

    # --------------------------------------------------------
    # Chuẩn hóa tên bác sĩ
    # --------------------------------------------------------

    doctor_name = body.doctor_name.strip()

    if not doctor_name:

        raise HTTPException(
            status_code=400,
            detail="Tên bác sĩ không được để trống"
        )

    # --------------------------------------------------------
    # Chuyển datetime thành chuỗi SQLite
    # --------------------------------------------------------

    appt_time = body.appt_time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # --------------------------------------------------------
    # INSERT
    # --------------------------------------------------------

    try:

        appt_id = execute(
            """
            INSERT INTO Appointments
            (
                UserId,
                DoctorName,
                Location,
                ApptTime,
                Content,
                Note,
                Status,
                RemindBefore,
                Channel,
                ReminderCount
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?,
                'upcoming',
                ?, ?,
                0
            )
            """,
            (
                user["UserId"],
                doctor_name,
                body.location,
                appt_time,
                body.content,
                body.note,
                body.remind_before,
                channel
            )
        )

    except Exception as e:

        print(
            "LỖI THÊM LỊCH TÁI KHÁM:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=f"Không thể thêm lịch tái khám: {e}"
        )

    return {
        "success": True,
        "message": "Đã thêm lịch tái khám",
        "appt_id": appt_id
    }


# ============================================================
# LẤY DANH SÁCH LỊCH TÁI KHÁM
# ============================================================

@router.get("/mine")
def get_my_appointments(
    user=Depends(current_user)
):

    appointments = query(
        """
        SELECT
            ApptId,
            DoctorName,
            Location,
            ApptTime,
            Content,
            Note,
            Status,
            RemindBefore,
            Channel,
            ConfirmedAt,
            ReminderCount,
            CreatedAt
        FROM Appointments
        WHERE UserId = ?
        ORDER BY ApptTime ASC
        """,
        (
            user["UserId"],
        )
    )

    return appointments


# ============================================================
# LẤY 1 LỊCH TÁI KHÁM
# ============================================================

@router.get("/{appt_id}")
def get_appointment(
    appt_id: int,
    user=Depends(current_user)
):

    appointment = get_user_appointment(
        appt_id,
        user["UserId"]
    )

    return appointment


# ============================================================
# XÁC NHẬN LỊCH
# ============================================================

@router.post("/{appt_id}/confirm")
def confirm_appointment(
    appt_id: int,
    user=Depends(current_user)
):

    appointment = get_user_appointment(
        appt_id,
        user["UserId"]
    )

    if appointment["Status"] == "cancelled":

        raise HTTPException(
            status_code=400,
            detail="Lịch này đã bị hủy"
        )

    execute(
        """
        UPDATE Appointments
        SET
            ConfirmedAt = ?,
            Status = 'upcoming'
        WHERE ApptId = ?
          AND UserId = ?
        """,
        (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            appt_id,
            user["UserId"]
        )
    )

    return {
        "success": True,
        "message": "Đã xác nhận lịch tái khám"
    }


# ============================================================
# ĐÁNH DẤU ĐÃ KHÁM
# ============================================================

@router.post("/{appt_id}/done")
def mark_done(
    appt_id: int,
    user=Depends(current_user)
):

    get_user_appointment(
        appt_id,
        user["UserId"]
    )

    execute(
        """
        UPDATE Appointments
        SET Status = 'done'
        WHERE ApptId = ?
          AND UserId = ?
        """,
        (
            appt_id,
            user["UserId"]
        )
    )

    return {
        "success": True,
        "message": "Đã đánh dấu hoàn thành lịch tái khám"
    }


# ============================================================
# ĐÁNH DẤU BỎ LỠ
# ============================================================

@router.post("/{appt_id}/missed")
def mark_missed(
    appt_id: int,
    user=Depends(current_user)
):

    get_user_appointment(
        appt_id,
        user["UserId"]
    )

    execute(
        """
        UPDATE Appointments
        SET Status = 'missed'
        WHERE ApptId = ?
          AND UserId = ?
        """,
        (
            appt_id,
            user["UserId"]
        )
    )

    return {
        "success": True,
        "message": "Đã đánh dấu bỏ lỡ lịch tái khám"
    }


# ============================================================
# HỦY LỊCH
# ============================================================

@router.patch("/{appt_id}/cancel")
def cancel_appointment(
    appt_id: int,
    user=Depends(current_user)
):

    get_user_appointment(
        appt_id,
        user["UserId"]
    )

    execute(
        """
        UPDATE Appointments
        SET Status = 'cancelled'
        WHERE ApptId = ?
          AND UserId = ?
        """,
        (
            appt_id,
            user["UserId"]
        )
    )

    return {
        "success": True,
        "message": "Đã hủy lịch tái khám"
    }


# ============================================================
# LỊCH TÁI KHÁM SẮP ĐẾN
# ============================================================

@router.get("/upcoming/list")
def upcoming_appointments(
    user=Depends(current_user)
):

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    appointments = query(
        """
        SELECT
            ApptId,
            DoctorName,
            Location,
            ApptTime,
            Content,
            Note,
            Status,
            RemindBefore,
            Channel,
            ConfirmedAt,
            ReminderCount,
            CreatedAt
        FROM Appointments
        WHERE UserId = ?
          AND ApptTime >= ?
          AND Status = 'upcoming'
        ORDER BY ApptTime ASC
        """,
        (
            user["UserId"],
            now
        )
    )

    return {
        "items": appointments
    }


# ============================================================
# KIỂM TRA LỊCH CẦN NHẮC
# ============================================================

@router.get("/due/list")
def due_appointments(
    user=Depends(current_user)
):

    now = datetime.now()

    appointments = query(
        """
        SELECT
            ApptId,
            DoctorName,
            Location,
            ApptTime,
            Content,
            Note,
            Status,
            RemindBefore,
            Channel,
            ConfirmedAt,
            ReminderCount,
            CreatedAt
        FROM Appointments
        WHERE UserId = ?
          AND Status = 'upcoming'
        ORDER BY ApptTime ASC
        """,
        (
            user["UserId"],
        )
    )

    due = []

    for appointment in appointments:

        try:

            appt_time = datetime.strptime(
                appointment["ApptTime"],
                "%Y-%m-%d %H:%M:%S"
            )

        except (ValueError, TypeError):

            continue

        remind_before = (
            appointment["RemindBefore"] or 0
        )

        remind_time = (
            appt_time -
            __import__("datetime").timedelta(
                minutes=remind_before
            )
        )

        # Đã đến thời điểm cần nhắc
        if remind_time <= now <= appt_time:

            due.append(
                appointment
            )

    return {
        "items": due
    }