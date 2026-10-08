from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from datetime import datetime, date, timedelta
from pathlib import Path
import uuid

from database import query, execute, get_conn
from auth import current_user


router = APIRouter(
    prefix="/api/medications",
    tags=["Medications"]
)


# ============================================================
# MODEL
# ============================================================

class MedicineIn(BaseModel):
    drug_name: str = Field(..., min_length=1)
    dosage: str | None = None
    times_per_day: int = Field(default=1, ge=1, le=12)
    start_date: str
    end_date: str | None = None
    note: str | None = None
    times: list[str] = Field(default_factory=list)


class StatusBody(BaseModel):
    status: str


# ============================================================
# HÀM HỖ TRỢ
# ============================================================

def normalize_time(value: str) -> str:
    """
    Chuẩn hóa giờ về HH:MM.

    Ví dụ:
        03:23       -> 03:23
        3:23        -> 03:23
        03:23:00    -> 03:23
        03:23 PM    -> 15:23
    """

    if not value:
        raise ValueError(
            "Giờ uống thuốc không được để trống"
        )

    value = value.strip()

    formats = [
        "%H:%M",
        "%H:%M:%S",
        "%I:%M %p",
        "%I:%M:%S %p"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%H:%M")
        except ValueError:
            pass

    raise ValueError(
        f"Giờ '{value}' không hợp lệ. "
        f"Vui lòng nhập dạng HH:MM."
    )


def parse_date(value: str) -> date:
    """
    Chuyển chuỗi YYYY-MM-DD thành date.
    """

    if not value:
        raise ValueError(
            "Ngày không được để trống"
        )

    value = value.strip()

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        raise ValueError(
            f"Ngày '{value}' không hợp lệ. "
            f"Vui lòng sử dụng định dạng YYYY-MM-DD."
        )


def make_scheduled_datetime(
    scheduled_date: date,
    time_text: str
) -> datetime:
    """
    Ghép ngày + giờ uống thuốc.
    """

    hour, minute = time_text.split(":")

    return datetime(
        scheduled_date.year,
        scheduled_date.month,
        scheduled_date.day,
        int(hour),
        int(minute),
        0
    )


# ============================================================
# THÊM LỊCH UỐNG THUỐC
# ============================================================

@router.post("")
def create_medicine(
    body: MedicineIn,
    user=Depends(current_user)
):
    """
    Thêm một thuốc và các giờ uống thuốc.

    Dùng SQLite:
        cursor.lastrowid
    """

    drug_name = body.drug_name.strip()

    if not drug_name:
        raise HTTPException(
            status_code=400,
            detail="Tên thuốc không được để trống"
        )

    # --------------------------------------------------------
    # Kiểm tra ngày
    # --------------------------------------------------------

    try:
        start_date = parse_date(body.start_date)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    end_date = None

    if body.end_date:
        try:
            end_date = parse_date(body.end_date)

        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    if end_date and end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail=(
                "Ngày kết thúc phải lớn hơn "
                "hoặc bằng ngày bắt đầu"
            )
        )

    # --------------------------------------------------------
    # Kiểm tra số lần/ngày
    # --------------------------------------------------------

    if body.times_per_day < 1 or body.times_per_day > 12:
        raise HTTPException(
            status_code=400,
            detail=(
                "Số lần uống trong ngày "
                "phải từ 1 đến 12"
            )
        )

    # --------------------------------------------------------
    # Kiểm tra danh sách giờ
    # --------------------------------------------------------

    if not body.times:
        raise HTTPException(
            status_code=400,
            detail=(
                "Vui lòng nhập ít nhất "
                "một giờ uống thuốc"
            )
        )

    normalized_times = []

    try:

        for value in body.times:

            normalized = normalize_time(value)

            # Kiểm tra giờ bị trùng
            if normalized in normalized_times:

                raise HTTPException(
                    status_code=400,
                    detail=f"Giờ {normalized} bị trùng"
                )

            normalized_times.append(normalized)

    except HTTPException:
        raise

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    # Số giờ phải bằng số lần/ngày
    if len(normalized_times) != body.times_per_day:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Số giờ uống thuốc "
                f"({len(normalized_times)}) "
                f"phải bằng số lần/ngày "
                f"({body.times_per_day})"
            )
        )

    normalized_times.sort()

    # --------------------------------------------------------
    # INSERT MEDICATION + MEDICATION TIMES
    # --------------------------------------------------------

    conn = get_conn()

    try:

        cur = conn.cursor()

        # ----------------------------------------------------
        # INSERT THUỐC
        # ----------------------------------------------------

        cur.execute(
            """
            INSERT INTO Medications
            (
                UserId,
                DrugName,
                Dosage,
                TimesPerDay,
                StartDate,
                EndDate,
                Note,
                IsActive
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["UserId"],
                drug_name,
                body.dosage,
                body.times_per_day,
                start_date.isoformat(),
                end_date.isoformat()
                if end_date else None,
                body.note,
                1
            )
        )

        # SQLite lấy ID vừa INSERT
        med_id = cur.lastrowid

        # ----------------------------------------------------
        # INSERT CÁC GIỜ UỐNG
        # ----------------------------------------------------

        for take_time in normalized_times:

            cur.execute(
                """
                INSERT INTO MedicationTimes
                (
                    MedId,
                    TakeTime
                )
                VALUES (?, ?)
                """,
                (
                    med_id,
                    take_time
                )
            )

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "LỖI THÊM THUỐC:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=f"Không thể thêm thuốc: {e}"
        )

    finally:
        conn.close()

    return {
        "success": True,
        "message": "Đã thêm thuốc",
        "med_id": med_id
    }


# ============================================================
# LẤY DANH SÁCH THUỐC CỦA USER
# ============================================================

@router.get("/mine")
def get_my_medications(
    user=Depends(current_user)
):
    """
    Lấy toàn bộ lịch thuốc của người dùng hiện tại.
    """

    medications = query(
        """
        SELECT
            MedId,
            UserId,
            DrugName,
            Dosage,
            TimesPerDay,
            StartDate,
            EndDate,
            Note,
            IsActive
        FROM Medications
        WHERE UserId = ?
        ORDER BY StartDate DESC, MedId DESC
        """,
        (user["UserId"],)
    )

    result = []

    for med in medications:

        times_rows = query(
            """
            SELECT
                TimeId,
                TakeTime
            FROM MedicationTimes
            WHERE MedId = ?
            ORDER BY TakeTime
            """,
            (med["MedId"],)
        )

        times = [
            row["TakeTime"]
            for row in times_rows
        ]

        time_text = ", ".join(times)

        frequency = (
            f"{med['TimesPerDay']} lần/ngày"
        )

        result.append(
            {
                "id": med["MedId"],
                "med_id": med["MedId"],

                "name": med["DrugName"],
                "drug_name": med["DrugName"],

                "dosage": med["Dosage"],

                "times": times,

                "time": time_text,

                "frequency": frequency,

                "times_per_day": med["TimesPerDay"],

                "start_date": med["StartDate"],
                "end_date": med["EndDate"],

                "note": med["Note"],

                "is_active": bool(
                    med["IsActive"]
                )
            }
        )

    return result


# ============================================================
# TẠO LOG ĐẾN GIỜ UỐNG
# ============================================================

def create_due_logs(user_id: int):
    """
    Kiểm tra các thuốc đến giờ uống.

    Khoảng kiểm tra:
        từ 1 phút trước
        đến 5 phút sau giờ uống.
    """

    now = datetime.now()

    today = now.date()

    medications = query(
        """
        SELECT
            MedId,
            UserId,
            DrugName,
            Dosage,
            TimesPerDay,
            StartDate,
            EndDate,
            Note
        FROM Medications
        WHERE UserId = ?
          AND IsActive = 1
        """,
        (user_id,)
    )

    due_items = []

    for med in medications:

        # ----------------------------------------------------
        # Kiểm tra ngày bắt đầu
        # ----------------------------------------------------

        try:

            start_date = parse_date(
                med["StartDate"]
            )

        except Exception:
            continue

        if today < start_date:
            continue

        # ----------------------------------------------------
        # Kiểm tra ngày kết thúc
        # ----------------------------------------------------

        if med["EndDate"]:

            try:

                end_date = parse_date(
                    med["EndDate"]
                )

            except Exception:
                continue

            if today > end_date:
                continue

        # ----------------------------------------------------
        # Lấy các giờ uống
        # ----------------------------------------------------

        times_rows = query(
            """
            SELECT TakeTime
            FROM MedicationTimes
            WHERE MedId = ?
            ORDER BY TakeTime
            """,
            (med["MedId"],)
        )

        for time_row in times_rows:

            try:

                take_time = normalize_time(
                    time_row["TakeTime"]
                )

                scheduled = make_scheduled_datetime(
                    today,
                    take_time
                )

            except Exception:
                continue

            # ------------------------------------------------
            # Khoảng thời gian cảnh báo
            # ------------------------------------------------

            window_start = (
                scheduled -
                timedelta(minutes=1)
            )

            window_end = (
                scheduled +
                timedelta(minutes=5)
            )

            if not (
                window_start <= now <= window_end
            ):
                continue

            scheduled_text = (
                scheduled.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            # ------------------------------------------------
            # Kiểm tra log đã tồn tại chưa
            # ------------------------------------------------

            existing = query(
                """
                SELECT
                    LogId,
                    Status,
                    ActionAt,
                    ProofImagePath
                FROM MedicationLogs
                WHERE MedId = ?
                  AND ScheduledAt = ?
                LIMIT 1
                """,
                (
                    med["MedId"],
                    scheduled_text
                ),
                one=True
            )

            if existing:

                # Đã xử lý rồi
                if existing["Status"] in (
                    "taken",
                    "missed",
                    "snoozed"
                ):
                    continue

                log_id = existing["LogId"]

            else:

                # ------------------------------------------------
                # Tạo log mới
                # ------------------------------------------------

                log_id = execute(
                    """
                    INSERT INTO MedicationLogs
                    (
                        MedId,
                        ScheduledAt,
                        Status
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        med["MedId"],
                        scheduled_text,
                        "pending"
                    )
                )

            due_items.append(
                {
                    "log_id": log_id,

                    "med_id": med["MedId"],

                    "medicine_id": med["MedId"],

                    "name": med["DrugName"],

                    "drug_name": med["DrugName"],

                    "dosage": med["Dosage"],

                    "take_time": take_time,

                    "scheduled_at": scheduled_text,

                    "status": "pending"
                }
            )

    return due_items


# ============================================================
# API: KIỂM TRA THUỐC ĐẾN GIỜ
# ============================================================

@router.get("/due")
def get_due_medications(
    user=Depends(current_user)
):

    items = create_due_logs(
        user["UserId"]
    )

    return {
        "items": items
    }


# ============================================================
# LẤY LOG UỐNG THUỐC
# ============================================================

@router.get("/logs")
def get_medication_logs(
    user=Depends(current_user)
):

    logs = query(
        """
        SELECT
            l.LogId,
            l.MedId,
            l.ScheduledAt,
            l.Status,
            l.ActionAt,
            l.ProofImagePath,
            m.DrugName,
            m.Dosage
        FROM MedicationLogs l
        INNER JOIN Medications m
            ON l.MedId = m.MedId
        WHERE m.UserId = ?
        ORDER BY l.ScheduledAt DESC
        """,
        (user["UserId"],)
    )

    return logs


# ============================================================
# KIỂM TRA LOG THUỘC USER
# ============================================================

def get_user_log(
    log_id: int,
    user_id: int
):

    log = query(
        """
        SELECT
            l.LogId,
            l.MedId,
            l.ScheduledAt,
            l.Status,
            l.ActionAt,
            l.ProofImagePath,
            m.DrugName,
            m.Dosage,
            m.UserId
        FROM MedicationLogs l
        INNER JOIN Medications m
            ON l.MedId = m.MedId
        WHERE l.LogId = ?
          AND m.UserId = ?
        """,
        (
            log_id,
            user_id
        ),
        one=True
    )

    if not log:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy lịch uống thuốc"
        )

    return log


# ============================================================
# CẬP NHẬT TRẠNG THÁI
# ============================================================

@router.post("/logs/{log_id}/status")
def update_log_status(
    log_id: int,
    body: StatusBody,
    user=Depends(current_user)
):

    allowed_statuses = {
        "pending",
        "taken",
        "missed",
        "snoozed"
    }

    if body.status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail="Trạng thái không hợp lệ"
        )

    get_user_log(
        log_id,
        user["UserId"]
    )

    action_at = None

    if body.status != "pending":

        action_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    execute(
        """
        UPDATE MedicationLogs
        SET
            Status = ?,
            ActionAt = ?
        WHERE LogId = ?
        """,
        (
            body.status,
            action_at,
            log_id
        )
    )

    return {
        "success": True,
        "message": "Đã cập nhật trạng thái",
        "status": body.status
    }


# ============================================================
# ĐÁNH DẤU ĐÃ UỐNG
# ============================================================

@router.post("/logs/{log_id}/taken")
def mark_taken(
    log_id: int,
    user=Depends(current_user)
):

    get_user_log(
        log_id,
        user["UserId"]
    )

    execute(
        """
        UPDATE MedicationLogs
        SET
            Status = 'taken',
            ActionAt = ?
        WHERE LogId = ?
        """,
        (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            log_id
        )
    )

    return {
        "success": True,
        "message": "Đã xác nhận uống thuốc"
    }


# ============================================================
# ĐÁNH DẤU QUÊN UỐNG
# ============================================================

@router.post("/logs/{log_id}/missed")
def mark_missed(
    log_id: int,
    user=Depends(current_user)
):

    get_user_log(
        log_id,
        user["UserId"]
    )

    execute(
        """
        UPDATE MedicationLogs
        SET
            Status = 'missed',
            ActionAt = ?
        WHERE LogId = ?
        """,
        (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            log_id
        )
    )

    return {
        "success": True,
        "message": "Đã đánh dấu bỏ lỡ"
    }


# ============================================================
# TẠM HOÃN
# ============================================================

@router.post("/logs/{log_id}/snooze")
def snooze(
    log_id: int,
    user=Depends(current_user)
):

    get_user_log(
        log_id,
        user["UserId"]
    )

    execute(
        """
        UPDATE MedicationLogs
        SET
            Status = 'snoozed',
            ActionAt = ?
        WHERE LogId = ?
        """,
        (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            log_id
        )
    )

    return {
        "success": True,
        "message": "Đã tạm hoãn nhắc thuốc"
    }


# ============================================================
# XÁC MINH BẰNG ẢNH
# ============================================================

@router.post("/logs/{log_id}/verify")
async def verify_medicine(
    log_id: int,
    file: UploadFile = File(...),
    user=Depends(current_user)
):
    """
    Nhận ảnh xác minh.

    Sau khi upload thành công:
        Status = taken
        ActionAt = thời gian hiện tại
        ProofImagePath = đường dẫn ảnh
    """

    # --------------------------------------------------------
    # Kiểm tra log thuộc user
    # --------------------------------------------------------

    get_user_log(
        log_id,
        user["UserId"]
    )

    # --------------------------------------------------------
    # Kiểm tra loại file
    # --------------------------------------------------------

    allowed_types = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp"
    }

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail=(
                "Ảnh không hợp lệ. "
                "Chỉ chấp nhận JPG, PNG hoặc WEBP."
            )
        )

    # --------------------------------------------------------
    # Đọc file
    # --------------------------------------------------------

    content = await file.read()

    # 10 MB
    max_size = 10 * 1024 * 1024

    if len(content) > max_size:

        raise HTTPException(
            status_code=400,
            detail="Ảnh không được vượt quá 10 MB"
        )

    if len(content) == 0:

        raise HTTPException(
            status_code=400,
            detail="Ảnh rỗng"
        )

    # --------------------------------------------------------
    # Tạo thư mục lưu ảnh
    # --------------------------------------------------------

    base_dir = Path(__file__).resolve().parent.parent

    proof_dir = (
        base_dir /
        "static" /
        "proofs"
    )

    proof_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Tạo tên file
    # --------------------------------------------------------

    extension = allowed_types[
        file.content_type
    ]

    filename = (
        f"{log_id}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    file_path = proof_dir / filename

    # --------------------------------------------------------
    # Lưu ảnh
    # --------------------------------------------------------

    try:

        with open(
            file_path,
            "wb"
        ) as f:

            f.write(content)

    except Exception as e:

        print(
            "LỖI LƯU ẢNH:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể lưu ảnh xác minh"
        )

    # --------------------------------------------------------
    # Đường dẫn dùng cho web
    # --------------------------------------------------------

    proof_url = (
        f"/static/proofs/{filename}"
    )

    # --------------------------------------------------------
    # Cập nhật log
    # --------------------------------------------------------

    action_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    execute(
        """
        UPDATE MedicationLogs
        SET
            Status = 'taken',
            ActionAt = ?,
            ProofImagePath = ?
        WHERE LogId = ?
        """,
        (
            action_at,
            proof_url,
            log_id
        )
    )

    return {
        "success": True,
        "message": (
            "Đã xác minh ảnh và "
            "xác nhận uống thuốc"
        ),
        "log_id": log_id,
        "status": "taken",
        "proof_image": proof_url
    }