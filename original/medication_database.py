import sqlite3


DATABASE = "medicine.db"


def connect_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            time TEXT NOT NULL,
            frequency TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_medicine(name, time, frequency):
    conn = connect_db()

    conn.execute("""
        INSERT INTO medicines
        (name, time, frequency)
        VALUES (?, ?, ?)
    """, (name, time, frequency))

    conn.commit()
    conn.close()


def get_medicines():
    conn = connect_db()

    medicines = conn.execute("""
        SELECT * FROM medicines
        ORDER BY time
    """).fetchall()

    conn.close()

    return medicines