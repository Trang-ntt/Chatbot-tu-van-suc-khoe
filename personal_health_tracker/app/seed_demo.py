from datetime import datetime,timedelta,timezone
import bcrypt
from .db import connect,init_db

def seed():
    init_db()
    users=[("admin_demo","AdminDemo!2026","admin"),("user_demo","UserDemo!2026","user"),("viewer_demo","ViewerDemo!2026","viewer")]
    with connect() as db:
        ids={}
        for name,pwd,role in users:
            row=db.execute("SELECT id FROM users WHERE username=?",(name,)).fetchone()
            if row: ids[name]=row["id"]
            else:
                c=db.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",(name,bcrypt.hashpw(pwd.encode(),bcrypt.gensalt()).decode(),role));ids[name]=c.lastrowid
        uid=ids["user_demo"]
        db.execute("INSERT OR IGNORE INTO profiles(user_id,full_name,birth_date,sex,height_cm,medical_history,health_goals) VALUES(?,?,?,?,?,?,?)",(uid,"Người dùng demo","2003-01-15","Không khai báo",165,"Dữ liệu giả lập","Theo dõi cân nặng và giấc ngủ"))
        if db.execute("SELECT COUNT(*) n FROM metrics WHERE user_id=?",(uid,)).fetchone()["n"]==0:
            now=datetime.now(timezone.utc)
            for i in range(14):
                t=(now-timedelta(days=13-i)).isoformat()
                db.execute("INSERT INTO metrics(user_id,metric,value,unit,measured_at,note) VALUES(?,?,?,?,?,?)",(uid,"weight",60+i*.08,"kg",t,"Dữ liệu giả lập"))
                db.execute("INSERT INTO metrics(user_id,metric,value,unit,measured_at,note) VALUES(?,?,?,?,?,?)",(uid,"sleep",7.2-(i%4)*.15,"hour",t,"Dữ liệu giả lập"))
        # No sharing is pre-authorized; user_demo must explicitly grant consent in the UI.
    print("Demo accounts seeded. Use only synthetic data.")
    print("admin_demo / AdminDemo!2026 | user_demo / UserDemo!2026 | viewer_demo / ViewerDemo!2026")

if __name__=="__main__":seed()
