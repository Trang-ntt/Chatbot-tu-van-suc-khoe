from flask import Flask, render_template, request, redirect, jsonify

from database import (
    create_database,
    add_medicine,
    get_medicines
)

from reminder import get_due_medicines


app = Flask(__name__)


# =========================
# TẠO DATABASE
# =========================

create_database()


# =========================
# TRANG CHÍNH
# =========================

@app.route("/")
def home():

    medicines = get_medicines()

    return render_template(
        "home.html",
        medicines=medicines
    )


# =========================
# THÊM LỊCH UỐNG THUỐC
# =========================

@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        name = request.form["name"]

        time = request.form["time"]

        frequency = request.form["frequency"]

        add_medicine(
            name,
            time,
            frequency
        )

        return redirect("/")

    return render_template(
        "add_medicine.html"
    )


# =========================
# TRANG KIỂM TRA THỦ CÔNG
# =========================

@app.route("/reminder")
def reminder():

    medicines = get_due_medicines()

    return render_template(
        "reminder.html",
        medicines=medicines
    )


# =========================
# API KIỂM TRA THUỐC ĐẾN GIỜ
# =========================

@app.route("/check-reminder")
def check_reminder():

    medicines = get_due_medicines()

    result = []

    for medicine in medicines:

        result.append({
            "id": medicine["id"],
            "name": medicine["name"],
            "time": medicine["time"],
            "frequency": medicine["frequency"]
        })

    return jsonify(result)


# =========================
# CHẠY CHƯƠNG TRÌNH
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )