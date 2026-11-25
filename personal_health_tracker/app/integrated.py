"""Secure symptom analysis, personal assistant, appointments and medication plans."""
import json
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .db import connect
from .main import current_user, only_user
from .symptom_engine import bot

router = APIRouter()
MAX_CHAT_TEXT = 2000


class SymptomStart(BaseModel):
    age: int = Field(ge=1, le=119)
    sex: str


class ChatMessage(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=MAX_CHAT_TEXT)


class AppointmentRequest(BaseModel):
    specialty: str = Field(min_length=2, max_length=100)
    preferred_at: str
    reason: str = Field(min_length=3, max_length=1000)
    note: str = Field(default="", max_length=1000)


class MedicationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    instructions: str = Field(default="", max_length=500)
    schedule_times: list[str] = Field(min_length=1, max_length=8)
    start_date: str
    end_date: str = ""
    repeat_rule: str = "daily"
    notes: str = Field(default="", max_length=500)


def _sex(value: str) -> str:
    s = (value or "").strip().lower()
    if s in {"nam", "male", "m"}:
        return "nam"
    if s in {"nữ", "nu", "female", "f"}:
        return "nu"
    raise HTTPException(400, "Chức năng mô hình hiện cần chọn giới tính nam hoặc nữ. Đây chỉ là thông tin đầu vào tham khảo.")


def _new_session(owner_id: Optional[int], age: int, sex: str) -> str:
    sid = uuid.uuid4().hex
    state = {"tuoi": age, "gioi": sex, "co": [], "khong": [], "da_hoi": [],
             "so_cau_hoi": 0, "cau_hoi_dang_cho": None, "canh_bao": False,
             "muc_canh_bao": None}
    with connect() as db:
        db.execute(
            "INSERT INTO chat_sessions(id,owner_id,age,sex,state_json) VALUES(?,?,?,?,?)",
            (sid, owner_id, age, sex, json.dumps(state, ensure_ascii=False))
        )
    return sid


def _result(state):
    kq = bot.tinh(set(state["co"]), set(state["khong"]), state["tuoi"], state["gioi"])
    diseases = []
    for score, idx in kq[:5]:
        original = bot.BENH[idx]
        diseases.append({
            "ten": bot.VI_BENH.get(original, original),
            "ten_goc": original,
            "diem_phu_hop": round(score * 100, 2),
            **bot.thong_tin_tuoi(original, state["tuoi"], state["gioi"])
        })
    return {
        "loai": "ket_qua",
        "trieu_chung_co": [bot.ten_tc(i) for i in sorted(state["co"])],
        "trieu_chung_khong": [bot.ten_tc(i) for i in sorted(state["khong"])],
        "danh_sach_benh": diseases,
        "nhom_tuoi_nguoi_dung": bot.nhom_tuoi(state["tuoi"]),
        "canh_bao": state["canh_bao"],
        "muc_canh_bao": state["muc_canh_bao"],
        "loi_khuyen": (
            "Điểm phù hợp là điểm tương đối trong nhóm bệnh của mô hình, không phải xác suất mắc bệnh "
            "thực tế hay chẩn đoán. Không tự dùng thuốc dựa trên kết quả; hãy liên hệ cơ sở y tế để được đánh giá."
        )
    }


def _continue(state):
    ranking = bot.tinh(set(state["co"]), set(state["khong"]), state["tuoi"], state["gioi"])
    state["da_hoi"] = sorted(set(state["da_hoi"]) | set(state["co"]) | set(state["khong"]))
    if state["so_cau_hoi"] >= 5:
        return _result(state)
    idx = bot.cau_hoi_tiep(ranking, set(state["da_hoi"]))
    if idx is None:
        return _result(state)
    state["da_hoi"].append(idx)
    state["cau_hoi_dang_cho"] = idx
    state["so_cau_hoi"] += 1
    return {"loai": "cau_hoi", "tin_nhan": f"Bạn có gặp triệu chứng “{bot.ten_tc(idx)}” không?"}


def _process(state, message):
    found, absent = bot.trich(message)
    state["co"] = sorted((set(state["co"]) | found) - absent)
    state["khong"] = sorted((set(state["khong"]) | absent) - set(state["co"]))
    warning = bot.phan_loai_canh_bao(message)
    if warning == "khan_cap":
        state["canh_bao"] = True
    if warning and (state["muc_canh_bao"] is None or warning == "khan_cap"):
        state["muc_canh_bao"] = warning
    if not state["co"] and not state["khong"]:
        return {"loai": "chua_hieu", "tin_nhan":
                "Mình chưa nhận diện được triệu chứng. Bạn thử mô tả ngắn như: sốt, ho, đau họng, nghẹt mũi hoặc khó thở nhé."}
    return _continue(state)


def _load_session(session_id, owner_id):
    with connect() as db:
        row = db.execute("SELECT * FROM chat_sessions WHERE id=?", (session_id,)).fetchone()
    if not row or row["owner_id"] != owner_id:
        raise HTTPException(404, "Không tìm thấy phiên trò chuyện hoặc bạn không có quyền truy cập.")
    if datetime.now(timezone.utc) - datetime.fromisoformat(row["created_at"].replace(" ", "T") + "+00:00") > timedelta(hours=12):
        raise HTTPException(410, "Phiên trò chuyện đã hết hạn. Hãy bắt đầu phiên mới.")
    return json.loads(row["state_json"])


def _message(session_id, owner_id, message):
    state = _load_session(session_id, owner_id)
    text = message.strip()
    if not text:
        raise HTTPException(400, "Bạn hãy nhập nội dung trước khi gửi.")
    waiting = state.get("cau_hoi_dang_cho")
    if waiting is not None:
        answer = bot.tra_loi_co_khong(text)
        if answer is not None:
            (state["co"] if answer else state["khong"]).append(waiting)
            state["co"] = sorted(set(state["co"]) - set(state["khong"]))
            state["khong"] = sorted(set(state["khong"]))
            state["cau_hoi_dang_cho"] = None
            response = _continue(state)
        else:
            state["cau_hoi_dang_cho"] = None
            response = _process(state, text)
    else:
        response = _process(state, text)
    with connect() as db:
        db.execute("UPDATE chat_sessions SET state_json=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                   (json.dumps(state, ensure_ascii=False), session_id))
    if state["muc_canh_bao"] == "khan_cap":
        response["canh_bao_cap_cuu"] = (
            "Có dấu hiệu có thể nguy hiểm. Hãy gọi cấp cứu hoặc đến cơ sở y tế gần nhất ngay; "
            "không chờ chatbot tiếp tục phân tích."
        )
    return response


def _personal_context(user_id):
    with connect() as db:
        profile = db.execute(
            "SELECT full_name,birth_date,sex,height_cm,medical_history,health_goals FROM profiles WHERE user_id=?",
            (user_id,)
        ).fetchone()
        rows = db.execute(
            "SELECT metric,value,secondary_value,unit,measured_at FROM metrics WHERE user_id=? "
            "ORDER BY measured_at DESC,id DESC LIMIT 20", (user_id,)
        ).fetchall()
    grouped = {}
    for row in rows:
        grouped.setdefault(row["metric"], []).append(dict(row))
    notes = []
    for metric, values in grouped.items():
        latest = values[0]
        label = {"blood_pressure": "huyết áp", "weight": "cân nặng", "glucose": "đường huyết",
                 "heart_rate": "nhịp tim", "sleep": "giấc ngủ"}.get(metric, metric)
        value = str(latest["value"])
        if latest["secondary_value"] is not None:
            value += "/" + str(latest["secondary_value"])
        notes.append(f"{label} gần nhất: {value} {latest['unit']} ({latest['measured_at']}).")
    return {
        "profile": dict(profile) if profile else {},
        "latest_metrics": grouped,
        "summary": " ".join(notes) if notes else "Chưa có chỉ số sức khỏe được ghi nhận."
    }


@router.post("/api/symptoms/start")
def start_guest_symptom(x: SymptomStart):
    sid = _new_session(None, x.age, _sex(x.sex))
    return {"session_id": sid, "tin_nhan": "Mình đã sẵn sàng. Bạn hãy mô tả triệu chứng đang gặp phải nhé.",
            "che_do": "guest"}


@router.post("/api/symptoms/message")
def guest_symptom_message(x: ChatMessage):
    return _message(x.session_id, None, x.message)


@router.post("/api/assistant/start")
def start_personal_assistant(u=Depends(only_user)):
    context = _personal_context(u["id"])
    profile = context["profile"]
    age = None
    if profile.get("birth_date"):
        try:
            born = date.fromisoformat(profile["birth_date"])
            today = date.today()
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        except ValueError:
            age = None
    if age is None or profile.get("sex") not in {"Nam", "Nữ"}:
        raise HTTPException(400, "Hãy cập nhật ngày sinh và giới tính Nam/Nữ trong Hồ sơ cá nhân trước khi dùng chatbot cá nhân. Bạn vẫn có thể dùng Phân tích triệu chứng độc lập.")
    sid = _new_session(u["id"], age, _sex(profile["sex"]))
    return {"session_id": sid, "tin_nhan":
            "Mình đã kết nối với hồ sơ và các chỉ số mới nhất của tài khoản bạn. Bạn có thể hỏi về xu hướng hoặc mô tả triệu chứng.",
            "health_context": context["summary"], "che_do": "personal"}


@router.post("/api/assistant/message")
def personal_assistant_message(x: ChatMessage, u=Depends(only_user)):
    response = _message(x.session_id, u["id"], x.message)
    context = _personal_context(u["id"])
    response["health_context"] = context["summary"]
    response["goi_y_chuc_nang"] = [
        {"label": "Xem xu hướng sức khỏe", "href": "#trends"},
        {"label": "Ghi chỉ số mới", "href": "#metrics"},
        {"label": "Đặt yêu cầu khám", "href": "#appointments"},
        {"label": "Quản lý thuốc và nhắc uống", "href": "#medications"}
    ]
    response["luu_y"] = (
        "Chatbot chỉ hỗ trợ tham khảo và hiển thị dữ liệu bạn đã nhập; không chẩn đoán, "
        "không kê đơn và không thay thế nhân viên y tế."
    )
    return response


@router.get("/api/appointments")
def list_appointments(u=Depends(only_user)):
    with connect() as db:
        return [dict(r) for r in db.execute(
            "SELECT * FROM appointments WHERE user_id=? ORDER BY created_at DESC", (u["id"],)
        ).fetchall()]


@router.post("/api/appointments")
def request_appointment(x: AppointmentRequest, u=Depends(only_user)):
    try:
        dt = datetime.fromisoformat(x.preferred_at.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(400, "Thời gian mong muốn phải theo định dạng ISO.")
    if dt <= datetime.now(timezone.utc) and dt.tzinfo is not None:
        raise HTTPException(400, "Hãy chọn thời gian trong tương lai.")
    with connect() as db:
        cur = db.execute(
            "INSERT INTO appointments(user_id,specialty,preferred_at,reason,note,status) VALUES(?,?,?,?,?,'pending')",
            (u["id"], x.specialty, x.preferred_at, x.reason, x.note)
        )
    return {"id": cur.lastrowid, "status": "pending",
            "message": "Đã lưu yêu cầu khám mô phỏng. Đây chưa phải lịch hẹn được bệnh viện xác nhận."}


@router.delete("/api/appointments/{appointment_id}")
def cancel_appointment(appointment_id: int, u=Depends(only_user)):
    with connect() as db:
        cur = db.execute(
            "UPDATE appointments SET status='cancelled' WHERE id=? AND user_id=? AND status='pending'",
            (appointment_id, u["id"])
        )
    if not cur.rowcount:
        raise HTTPException(404, "Không tìm thấy yêu cầu đang chờ.")
    return {"message": "Đã hủy yêu cầu."}


@router.get("/api/medications")
def list_medications(u=Depends(only_user)):
    with connect() as db:
        return [dict(r) for r in db.execute(
            "SELECT * FROM medications WHERE user_id=? AND active=1 ORDER BY start_date,name", (u["id"],)
        ).fetchall()]


@router.post("/api/medications")
def add_medication(x: MedicationRequest, u=Depends(only_user)):
    try:
        start = date.fromisoformat(x.start_date)
        end = date.fromisoformat(x.end_date) if x.end_date else None
    except ValueError:
        raise HTTPException(400, "Ngày bắt đầu/kết thúc phải theo định dạng YYYY-MM-DD.")
    if end and end < start:
        raise HTTPException(400, "Ngày kết thúc không thể trước ngày bắt đầu.")
    if x.repeat_rule not in {"daily", "weekly", "once"}:
        raise HTTPException(400, "Chu kỳ nhắc không hợp lệ.")
    times = []
    for t in x.schedule_times:
        try:
            datetime.strptime(t, "%H:%M")
        except ValueError:
            raise HTTPException(400, "Giờ nhắc phải theo dạng HH:MM.")
        if t not in times:
            times.append(t)
    with connect() as db:
        cur = db.execute(
            "INSERT INTO medications(user_id,name,instructions,schedule_times,start_date,end_date,repeat_rule,notes) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (u["id"], x.name, x.instructions, json.dumps(times), x.start_date, x.end_date, x.repeat_rule, x.notes)
        )
    return {"id": cur.lastrowid, "message":
            "Đã lưu lịch nhắc. Tên thuốc, hướng dẫn và giờ uống phải theo đơn/chỉ dẫn của nhân viên y tế."}


@router.delete("/api/medications/{medication_id}")
def deactivate_medication(medication_id: int, u=Depends(only_user)):
    with connect() as db:
        cur = db.execute("UPDATE medications SET active=0 WHERE id=? AND user_id=? AND active=1",
                         (medication_id, u["id"]))
    if not cur.rowcount:
        raise HTTPException(404, "Không tìm thấy lịch thuốc đang hoạt động.")
    return {"message": "Đã tắt lịch nhắc."}


@router.get("/api/medications/due")
def due_medications(u=Depends(only_user)):
    now = datetime.now()
    today = now.date().isoformat()
    clock = now.strftime("%H:%M")
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM medications WHERE user_id=? AND active=1 AND start_date<=? "
            "AND (end_date='' OR end_date IS NULL OR end_date>=?)",
            (u["id"], today, today)
        ).fetchall()
    due = []
    for row in rows:
        times = json.loads(row["schedule_times"])
        if clock in times and (row["repeat_rule"] != "weekly" or now.weekday() == 0):
            due.append({"id": row["id"], "name": row["name"], "time": clock,
                        "instructions": row["instructions"]})
    return due


@router.post("/api/medications/{medication_id}/taken")
def mark_medication_taken(medication_id: int, u=Depends(only_user)):
    with connect() as db:
        med = db.execute("SELECT id FROM medications WHERE id=? AND user_id=? AND active=1",
                         (medication_id, u["id"])).fetchone()
        if not med:
            raise HTTPException(404, "Không tìm thấy lịch thuốc.")
        db.execute("INSERT INTO medication_logs(user_id,medication_id,taken_at) VALUES(?,?,?)",
                   (u["id"], medication_id, datetime.now(timezone.utc).isoformat()))
    return {"message": "Đã ghi nhận bạn đánh dấu đã uống."}
