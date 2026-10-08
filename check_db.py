import sqlite3

conn = sqlite3.connect("healthbot.db")

tables = [
    "Users",
    "ChatHistory",
    "Medications",
    "MedicationTimes",
    "MedicationLogs",
    "Appointments",
    "Symptoms",
    "SymptomChecks",
    "Notifications"
]

for table in tables:
    print("\n================================")
    print("BẢNG:", table)
    print("================================")

    rows = conn.execute(
        f"PRAGMA table_info({table})"
    ).fetchall()

    if not rows:
        print("KHÔNG TỒN TẠI BẢNG")
    else:
        for row in rows:
            print(
                "Tên cột:",
                row[1],
                "| Kiểu:",
                row[2]
            )

conn.close()