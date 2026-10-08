from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db

from routers import (
    auth,
    chatbot,
    symptoms,
    medicines,
    appointments,
    notifications,
    reports,
    admin
)

app = FastAPI(
    title="HealthBot - Hệ thống tích hợp",
    description="Chatbot AI tư vấn sức khỏe, phân tích triệu chứng, nhắc uống thuốc và quản lý lịch tái khám.",
    version="1.0.0"
)

# Khởi tạo database
init_db()

# =========================
# API ROUTERS
# =========================

app.include_router(auth.router)
app.include_router(chatbot.router)
app.include_router(symptoms.router)
app.include_router(medicines.router)
app.include_router(appointments.router)
app.include_router(notifications.router)
app.include_router(reports.router)
app.include_router(admin.router)

# =========================
# STATIC
# =========================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# =========================
# FRONTEND
# =========================

@app.get("/", include_in_schema=False)
def index():
    return FileResponse("static/index.html")


@app.get("/home", include_in_schema=False)
def home():
    return FileResponse("static/home.html")


@app.get("/chat", include_in_schema=False)
def chat_page():
    return FileResponse("static/chat.html")


@app.get("/symptoms", include_in_schema=False)
def symptoms_page():
    return FileResponse("static/symptoms.html")


@app.get("/medications", include_in_schema=False)
def medications_page():
    return FileResponse("static/medications.html")


@app.get("/appointments", include_in_schema=False)
def appointments_page():
    return FileResponse("static/appointments.html")


@app.get("/add", include_in_schema=False)
def add_medicine_page():
    return FileResponse("static/add_medicine.html")


# =========================
# TEST API
# =========================

@app.get("/api/test")
def test_server():
    return {
        "success": True,
        "message": "HealthBot API đang hoạt động",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Server đang chạy tại: http://localhost:8000")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
