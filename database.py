import sqlite3
from pathlib import Path


# ============================================================
# ĐƯỜNG DẪN DATABASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "healthbot.db"


# ============================================================
# KẾT NỐI SQLITE
# ============================================================

def get_conn():

    conn = sqlite3.connect(
        str(DB_PATH)
    )

    # Cho phép truy cập dữ liệu dạng:
    # row["UserId"]
    conn.row_factory = sqlite3.Row

    # Bật khóa ngoại
    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


# ============================================================
# QUERY
# ============================================================

def query(
    sql,
    params=(),
    one=False,
    commit=False
):

    conn = get_conn()

    try:

        cur = conn.cursor()

        cur.execute(
            sql,
            params
        )

        # Nếu chỉ là INSERT / UPDATE / DELETE
        if commit:

            conn.commit()

            return None

        # Không có dữ liệu trả về
        if cur.description is None:

            return None

        rows = [
            dict(row)
            for row in cur.fetchall()
        ]

        if one:

            return (
                rows[0]
                if rows
                else None
            )

        return rows

    finally:

        conn.close()


# ============================================================
# EXECUTE
# ============================================================

def execute(
    sql,
    params=()
):

    conn = get_conn()

    try:

        cur = conn.cursor()

        cur.execute(
            sql,
            params
        )

        conn.commit()

        return cur.lastrowid

    finally:

        conn.close()


# ============================================================
# EXECUTESCRIPT
# ============================================================

def executescript(
    sql_script
):

    conn = get_conn()

    try:

        conn.executescript(
            sql_script
        )

        conn.commit()

    finally:

        conn.close()


# ============================================================
# KHỞI TẠO DATABASE
# ============================================================

def init_db():

    conn = get_conn()

    try:

        cur = conn.cursor()

        # ====================================================
        # USERS
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Users
            (
                UserId INTEGER PRIMARY KEY AUTOINCREMENT,

                Username TEXT NOT NULL UNIQUE,

                PasswordHash TEXT NOT NULL,

                FullName TEXT NOT NULL,

                Email TEXT NOT NULL UNIQUE,

                Phone TEXT,

                Role TEXT NOT NULL
                    DEFAULT 'user',

                IsActive INTEGER NOT NULL
                    DEFAULT 1,

                CreatedAt TEXT
                    DEFAULT CURRENT_TIMESTAMP,

                LastLoginAt TEXT
            )
            """
        )


        # ====================================================
        # CHAT HISTORY
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ChatHistory
            (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,

                UserID INTEGER NOT NULL,

                Message TEXT NOT NULL,

                Response TEXT,

                CreatedAt TEXT
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(UserID)
                    REFERENCES Users(UserId)
                    ON DELETE CASCADE
            )
            """
        )


        # ====================================================
        # MEDICATIONS
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Medications
            (
                MedId INTEGER PRIMARY KEY AUTOINCREMENT,

                UserId INTEGER NOT NULL,

                DrugName TEXT NOT NULL,

                Dosage TEXT,

                TimesPerDay INTEGER NOT NULL
                    DEFAULT 1,

                StartDate TEXT NOT NULL,

                EndDate TEXT,

                Note TEXT,

                IsActive INTEGER NOT NULL
                    DEFAULT 1,

                FOREIGN KEY(UserId)
                    REFERENCES Users(UserId)
                    ON DELETE CASCADE
            )
            """
        )


        # ====================================================
        # MEDICATION TIMES
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS MedicationTimes
            (
                TimeId INTEGER PRIMARY KEY AUTOINCREMENT,

                MedId INTEGER NOT NULL,

                TakeTime TEXT NOT NULL,

                FOREIGN KEY(MedId)
                    REFERENCES Medications(MedId)
                    ON DELETE CASCADE
            )
            """
        )


        # ====================================================
        # MEDICATION LOGS
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS MedicationLogs
            (
                LogId INTEGER PRIMARY KEY AUTOINCREMENT,

                MedId INTEGER NOT NULL,

                ScheduledAt TEXT NOT NULL,

                Status TEXT NOT NULL
                    DEFAULT 'pending',

                ActionAt TEXT,

                ProofImagePath TEXT,

                FOREIGN KEY(MedId)
                    REFERENCES Medications(MedId)
                    ON DELETE CASCADE,

                CHECK
                (
                    Status IN
                    (
                        'pending',
                        'taken',
                        'missed',
                        'snoozed'
                    )
                )
            )
            """
        )


        # ====================================================
        # APPOINTMENTS
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Appointments
            (
                ApptId INTEGER PRIMARY KEY AUTOINCREMENT,

                UserId INTEGER NOT NULL,

                DoctorName TEXT NOT NULL,

                Location TEXT,

                ApptTime TEXT NOT NULL,

                Content TEXT,

                Note TEXT,

                Status TEXT NOT NULL
                    DEFAULT 'upcoming',

                RemindBefore INTEGER NOT NULL
                    DEFAULT 1440,

                Channel TEXT NOT NULL
                    DEFAULT 'web',

                ConfirmedAt TEXT,

                ReminderCount INTEGER NOT NULL
                    DEFAULT 0,

                CreatedAt TEXT
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(UserId)
                    REFERENCES Users(UserId)
                    ON DELETE CASCADE,

                CHECK
                (
                    Status IN
                    (
                        'upcoming',
                        'done',
                        'cancelled',
                        'missed'
                    )
                )
            )
            """
        )


        # ====================================================
        # SYMPTOMS
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Symptoms
            (
                SymptomId INTEGER PRIMARY KEY AUTOINCREMENT,

                UserId INTEGER NOT NULL,

                SymptomName TEXT NOT NULL,

                Description TEXT,

                Severity INTEGER,

                CreatedAt TEXT
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(UserId)
                    REFERENCES Users(UserId)
                    ON DELETE CASCADE
            )
            """
        )


        # ====================================================
        # SYMPTOM CHECKS
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS SymptomChecks
            (
                CheckId INTEGER PRIMARY KEY AUTOINCREMENT,

                UserId INTEGER NOT NULL,

                SymptomText TEXT NOT NULL,

                Severity INTEGER,

                DaysSince INTEGER,

                ResultJson TEXT,

                CreatedAt TEXT
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(UserId)
                    REFERENCES Users(UserId)
                    ON DELETE CASCADE
            )
            """
        )


        # ====================================================
        # NOTIFICATIONS
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Notifications
            (
                NotificationId INTEGER PRIMARY KEY AUTOINCREMENT,

                UserId INTEGER NOT NULL,

                Title TEXT NOT NULL,

                Message TEXT NOT NULL,

                NotificationType TEXT
                    DEFAULT 'web',

                SentAt TEXT
                    DEFAULT CURRENT_TIMESTAMP,

                Status TEXT
                    DEFAULT 'unread',

                FOREIGN KEY(UserId)
                    REFERENCES Users(UserId)
                    ON DELETE CASCADE
            )
            """
        )


        # ====================================================
        # CONDITIONS
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Conditions
            (
                ConditionId INTEGER PRIMARY KEY AUTOINCREMENT,

                ConditionName TEXT NOT NULL UNIQUE,

                Description TEXT
            )
            """
        )


        # ====================================================
        # CONDITION - SYMPTOM
        # ====================================================

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ConditionSymptoms
            (
                ConditionId INTEGER NOT NULL,

                SymptomId INTEGER NOT NULL,

                PRIMARY KEY
                (
                    ConditionId,
                    SymptomId
                ),

                FOREIGN KEY(ConditionId)
                    REFERENCES Conditions(ConditionId)
                    ON DELETE CASCADE,

                FOREIGN KEY(SymptomId)
                    REFERENCES Symptoms(SymptomId)
                    ON DELETE CASCADE
            )
            """
        )


        # ====================================================
        # TẠO INDEX
        # ====================================================

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_chat_user
            ON ChatHistory(UserID)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_med_user
            ON Medications(UserId)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_medlog_med
            ON MedicationLogs(MedId)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_appt_user
            ON Appointments(UserId)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_symptom_user
            ON SymptomChecks(UserId)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_notification_user
            ON Notifications(UserId)
            """
        )


        # ====================================================
        # LƯU DATABASE
        # ====================================================

        conn.commit()

        print(
            "SQLite database đã được khởi tạo."
        )

        print(
            f"Database: {DB_PATH}"
        )

    except Exception as e:

        conn.rollback()

        print(
            "LỖI KHỞI TẠO DATABASE:",
            e
        )

        raise

    finally:

        conn.close()


# ============================================================
# CHẠY TRỰC TIẾP FILE
# ============================================================

if __name__ == "__main__":

    init_db()