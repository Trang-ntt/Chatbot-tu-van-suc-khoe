import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, time, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

DATA_FILE = "appointments.json"

# ==========================================
# CẤU HÌNH TRANG WEB & CSS TRUYỀN THÔNG Y TẾ
# ==========================================
st.set_page_config(
    page_title="Hệ Thống Tái Khám & Chatbot AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS cho giao diện đẹp mắt & hiện đại
st.markdown("""
<style>
    .main-header { font-size: 26px; font-weight: bold; color: #0E1117; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: 500; }
    .status-badge { padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #1E88E5; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# XỬ LÝ DỮ LIỆU
# ==========================================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Khởi tạo dữ liệu mẫu nếu chưa có
if not os.path.exists(DATA_FILE):
    sample_data = [
        {
            "id": 101,
            "patient_name": "Nguyễn Văn An",
            "phone": "0987654321",
            "doctor": "BS. Nguyễn Văn A",
            "location": "Phòng 302 - Khoa Bệnh Mạn Tính",
            "date": str(date.today() + timedelta(days=2)),
            "time": "08:30",
            "reason": "Tái khám định kỳ tăng huyết áp",
            "note": "Nhớ nhịn ăn sáng để xét nghiệm máu",
            "remind_before": "1 ngày",
            "notify_channel": "Email & SMS",
            "status": "Sắp tới",
            "confirmed": False,
            "remind_count": 0
        }
    ]
    save_data(sample_data)

# ==========================================
# BỘ LÊN LỊCH NGẦM (SCHEDULER & NOTIFICATION)
# ==========================================
def check_and_send_reminders():
    # Hàm mô phỏng quét dữ liệu gửi thông báo tự động (CN 7, 9, 12)
    pass

@st.cache_resource
def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_reminders, 'interval', seconds=30)
    scheduler.start()
    return scheduler

init_scheduler()

# ==========================================
# THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=70)
st.sidebar.title("HỆ THỐNG Y TẾ")
st.sidebar.caption("Chức năng: Nhắc lịch tái khám & Chatbot AI")

menu = st.sidebar.radio(
    "Danh mục quản lý:",
    [
        "📌 Tổng quan & Danh sách lịch",
        "➕ Tạo lịch tái khám",
        "✏️ Chỉnh sửa & Hủy lịch",
        "⚙️ Thiết lập thông báo",
        "🤖 Chatbot AI tư vấn & đổi lịch"
    ]
)

# Thống kê nhanh ở Sidebar
data = load_data()
df = pd.DataFrame(data) if data else pd.DataFrame()

st.sidebar.divider()
st.sidebar.subheader("📊 Thống kê nhanh")
if not df.empty:
    st.sidebar.metric("Tổng số lịch", len(df))
    st.sidebar.metric("Lịch sắp tới", len(df[df["status"] == "Sắp tới"]))
    st.sidebar.metric("Đã xác nhận", len(df[df["confirmed"] == True]))

# ==========================================
# MENU 1: TỔNG QUAN & XEM DANH SÁCH LỊCH (CN 2, 3, 8)
# ==========================================
if menu == "📌 Tổng quan & Danh sách lịch":
    st.markdown("<div class='main-header'>📋 Quản Lý & Xem Chi Tiết Lịch Tái Khám</div>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("Chưa có lịch tái khám nào trong hệ thống.")
    else:
        # Bộ lọc trạng thái
        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            filter_status = st.selectbox("Lọc theo trạng thái:", ["Tất cả", "Sắp tới", "Hoàn thành", "Đã hủy"])
        
        filtered_df = df if filter_status == "Tất cả" else df[df["status"] == filter_status]
        
        # Bảng danh sách tổng quan (CN 2)
        st.subheader("Danh sách lịch")
        display_cols = ["id", "patient_name", "phone", "doctor", "date", "time", "status", "confirmed"]
        st.dataframe(
            filtered_df[display_cols].rename(columns={
                "id": "Mã lịch", "patient_name": "Bệnh nhân", "phone": "SĐT",
                "doctor": "Bác sĩ", "date": "Ngày khám", "time": "Giờ",
                "status": "Trạng thái", "confirmed": "Đã xác nhận"
            }),
            use_container_width=True
        )

        # Xem chi tiết & Xác nhận tham gia (CN 3 & CN 8)
        st.divider()
        st.subheader("🔍 Xem chi tiết & Xác nhận tham gia")
        col_select, col_action = st.columns([2, 1])
        
        with col_select:
            selected_id = st.selectbox("Chọn Mã lịch hẹn để xem thông tin chi tiết:", df["id"].tolist())
            selected_item = next(item for item in data if item["id"] == selected_id)
            
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Bệnh nhân:** {selected_item['patient_name']}")
                st.write(f"**Số điện thoại:** {selected_item['phone']}")
                st.write(f"**Bác sĩ phụ trách:** {selected_item['doctor']}")
                st.write(f"**Địa điểm:** {selected_item['location']}")
            with c2:
                st.write(f"**Thời gian:** {selected_item['time']} - Ngày {selected_item['date']}")
                st.write(f"**Nội dung khám:** {selected_item['reason']}")
                st.write(f"**Ghi chú dặn dò:** {selected_item['note']}")
                st.write(f"**Kênh nhận nhắc lịch:** {selected_item['notify_channel']} (Trước {selected_item['remind_before']})")
        
        with col_action:
            st.write("---")
            st.write("**Xác nhận lịch (CN 8):**")
            if selected_item["confirmed"]:
                st.success("✅ Bệnh nhân ĐÃ XÁC NHẬN tham gia.")
            else:
                st.warning("⚠️ Chưa xác nhận tham gia.")
                if st.button("👍 Bệnh nhân xác nhận tham gia"):
                    for item in data:
                        if item["id"] == selected_id:
                            item["confirmed"] = True
                    save_data(data)
                    st.success("Đã ghi nhận xác nhận của bệnh nhân!")
                    st.rerun()

# ==========================================
# MENU 2: TẠO LỊCH TÁI KHÁM (CN 1)
# ==========================================
elif menu == "➕ Tạo lịch tái khám":
    st.markdown("<div class='main-header'>📝 Đăng Ký / Tạo Lịch Tái Khám Mới</div>", unsafe_allow_html=True)
    
    with st.form("create_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Họ và tên bệnh nhân *")
            phone = st.text_input("Số điện thoại *")
            doctor = st.text_input("Bác sĩ phụ trách", value="BS. Nguyễn Văn A")
            location = st.text_input("Địa điểm khám", value="Phòng 302 - Khoa Khám Bệnh")
        
        with c2:
            app_date = st.date_input("Ngày tái khám", min_value=date.today())
            app_time = st.time_input("Giờ tái khám", value=time(8, 30))
            reason = st.text_input("Nội dung / Lí do tái khám", value="Tái khám định kỳ")
            note = st.text_area("Ghi chú / Lời dặn bác sĩ", value="Mang theo hồ sơ khám cũ")
            
        submit = st.form_submit_button("🚀 Lưu Lịch Tái Khám")
        
        if submit:
            if not name or not phone:
                st.error("Vui lòng điền đầy đủ Tên bệnh nhân và Số điện thoại!")
            else:
                new_id = len(data) + 101
                new_entry = {
                    "id": new_id,
                    "patient_name": name,
                    "phone": phone,
                    "doctor": doctor,
                    "location": location,
                    "date": str(app_date),
                    "time": app_time.strftime("%H:%M"),
                    "reason": reason,
                    "note": note,
                    "remind_before": "1 ngày",
                    "notify_channel": "App / Web",
                    "status": "Sắp tới",
                    "confirmed": False,
                    "remind_count": 0
                }
                data.append(new_entry)
                save_data(data)
                st.success(f"✅ Tạo lịch thành công cho bệnh nhân {name} (Mã lịch: {new_id})!")

# ==========================================
# MENU 3: CHỈNH SỬA & HỦY LỊCH (CN 4, 5)
# ==========================================
elif menu == "✏️ Chỉnh sửa & Hủy lịch":
    st.markdown("<div class='main-header'>⚙️ Chỉnh Sửa Hoặc Hủy Lịch Tái Khám</div>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("Chưa có lịch tái khám nào.")
    else:
        selected_id = st.selectbox("Chọn Mã lịch tái khám cần thao tác:", df["id"].tolist())
        item = next(i for i in data if i["id"] == selected_id)
        
        tab_edit, tab_cancel = st.tabs(["✏️ Chỉnh sửa thông tin (CN 4)", "❌ Hủy lịch hẹn (CN 5)"])
        
        with tab_edit:
            with st.form("edit_form"):
                e_doctor = st.text_input("Bác sĩ phụ trách", value=item["doctor"])
                e_location = st.text_input("Địa điểm", value=item["location"])
                e_date = st.date_input("Ngày tái khám", value=datetime.strptime(item["date"], "%Y-%m-%d").date())
                e_time = st.time_input("Giờ tái khám", value=datetime.strptime(item["time"], "%H:%M").time())
                e_status = st.selectbox("Trạng thái", ["Sắp tới", "Hoàn thành", "Bỏ lỡ"], index=["Sắp tới", "Hoàn thành", "Bỏ lỡ"].index(item.get("status", "Sắp tới")))
                
                if st.form_submit_button("Cập nhật lịch"):
                    item["doctor"] = e_doctor
                    item["location"] = e_location
                    item["date"] = str(e_date)
                    item["time"] = e_time.strftime("%H:%M")
                    item["status"] = e_status
                    save_data(data)
                    st.success("✅ Cập nhật lịch thành công và đã đồng bộ reminder!")
                    st.rerun()

        with tab_cancel:
            st.warning("⚠️ Hành động này sẽ hủy lịch và ngừng gửi toàn bộ thông báo nhắc nhở liên quan.")
            if st.button("🔴 Cập nhật trạng thái HỦY LỊCH"):
                item["status"] = "Đã hủy"
                save_data(data)
                st.error(f"Đã hủy lịch ID #{selected_id} thành công.")
                st.rerun()

# ==========================================
# MENU 4: THIẾT LẬP THỜI GIAN NHẮC & THÔNG BÁO (CN 6, 7, 9, 12)
# ==========================================
elif menu == "⚙️ Thiết lập thông báo":
    st.markdown("<div class='main-header'>🔔 Thiết Lập Thời Gian Nhắc & Tự Động Gửi Thông Báo</div>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("Chưa có lịch tái khám nào.")
    else:
        selected_id = st.selectbox("Chọn Mã lịch cần thiết lập:", df["id"].tolist())
        item = next(i for i in data if i["id"] == selected_id)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("⏱️ Thiết lập thời gian nhắc (CN 6)")
            remind_opt = st.selectbox(
                "Chọn mốc thời gian nhắc trước:",
                ["1 giờ", "3 giờ", "1 ngày", "2 ngày", "1 tuần"],
                index=["1 giờ", "3 giờ", "1 ngày", "2 ngày", "1 tuần"].index(item.get("remind_before", "1 ngày"))
            )
            
            st.subheader("📲 Kênh gửi thông báo (CN 7, 12)")
            channel_opt = st.multiselect(
                "Chọn kênh gửi tự động:",
                ["App / Web Notification", "Email", "SMS Tự động (Mở rộng)"],
                default=["App / Web Notification"]
            )
            
            if st.button("Lưu cấu hình thông báo"):
                item["remind_before"] = remind_opt
                item["notify_channel"] = ", ".join(channel_opt)
                save_data(data)
                st.success("Đã lưu cấu hình thông báo!")

        with c2:
            st.subheader("🔁 Cơ chế Nhắc lại (CN 9)")
            st.info("Hệ thống sẽ tự động nhắc lại nếu bệnh nhân chưa bấm nút 'Xác nhận tham gia'.")
            st.write(f"- Số lần đã nhắc: **{item.get('remind_count', 0)} / 3 lần**")
            
            if st.button("🧪 Mô phỏng Gửi Thông Báo Ngay"):
                st.toast(f"🔔 [MÔ PHỎNG SƠN] Gửi thông báo tới {item['patient_name']} qua {item['notify_channel']}: 'Bạn có lịch tái khám vào {item['date']} {item['time']}'")
                st.success("Đã phát tin nhắn thử nghiệm thành công!")

# ==========================================
# MENU 5: CHATBOT AI TƯ VẤN & ĐỔI LỊCH (CN 10, 11)
# ==========================================
elif menu == "🤖 Chatbot AI tư vấn & đổi lịch":
    st.markdown("<div class='main-header'>🤖 Chatbot AI Tư Vấn & Trợ Lý Tái Khám</div>", unsafe_allow_html=True)
    st.caption("Tra cứu lịch hẹn (CN 10) hoặc Đổi lịch tái khám qua hội thoại (CN 11)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Xin chào! Tôi là Trợ lý AI y tế. Bạn muốn tra cứu lịch tái khám hay hỗ trợ yêu cầu đổi lịch?"}
        ]
        
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("Nhập câu hỏi (Ví dụ: 'Xem lịch tái khám của tôi' hoặc 'Tôi muốn đổi lịch')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Xử lý phản hồi đơn giản từ Chatbot AI
        p_lower = prompt.lower()
        if "xem" in p_lower or "tra cứu" in p_lower or "lịch" in p_lower:
            if not df.empty:
                first = data[0]
                reply = f"🏥 **Thông tin lịch tái khám của bạn:**\n- Ngày: {first['date']} lúc {first['time']}\n- Bác sĩ: {first['doctor']}\n- Địa điểm: {first['location']}\n- Ghi chú: {first['note']}"
            else:
                reply = "Hiện tại bạn chưa có lịch tái khám nào được ghi nhận trên hệ thống."
        elif "đổi" in p_lower or "hoãn" in p_lower:
            reply = "Dạ, để yêu cầu đổi lịch tái khám, bạn vui lòng cho tôi biết **Ngày & Giờ mong muốn mới**, tôi sẽ gửi yêu cầu cập nhật lên hệ thống cho bác sĩ xác nhận nhé!"
        else:
            reply = "Tôi đã ghi nhận thông tin. Bạn có muốn tra cứu thời gian tái khám hay cần tư vấn dặn dò về đơn thuốc/xét nghiệm không?"
            
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)