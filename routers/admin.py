from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import current_user
from database import query, execute

router=APIRouter(prefix='/api/admin',tags=['Admin'])

def admin_only(u=Depends(current_user)):
    if u['Role']!='admin': raise HTTPException(403,'Chỉ quản trị viên được truy cập')
    return u

@router.get('/stats')
def stats(_=Depends(admin_only)):
    return query('''SELECT COUNT(*) AS total,
      SUM(CASE WHEN IsActive=1 THEN 1 ELSE 0 END) AS active,
      SUM(CASE WHEN Role='admin' THEN 1 ELSE 0 END) AS admins FROM Users''',one=True)

@router.get('/conversations')
def conversations(_=Depends(admin_only)):
    return query('''SELECT TOP 200 c.ConvId,u.FullName,c.Sender,c.Message,c.CreatedAt
      FROM Conversations c JOIN Users u ON u.UserId=c.UserId ORDER BY c.CreatedAt DESC''')

@router.get('/medications')
def medications(_=Depends(admin_only)):
    return query('''SELECT m.MedId,u.FullName,m.DrugName,m.Dosage,m.TimesPerDay,m.StartDate,m.EndDate,m.IsActive
      FROM Medications m JOIN Users u ON u.UserId=m.UserId ORDER BY m.StartDate DESC''')

@router.get('/symptom-checks')
def symptom_checks(_=Depends(admin_only)):
    return query('''SELECT TOP 200 s.CheckId,u.FullName,s.SymptomText,s.Severity,s.DaysSince,s.CreatedAt
      FROM SymptomChecks s JOIN Users u ON u.UserId=s.UserId ORDER BY s.CreatedAt DESC''')

@router.get('/appointments')
def appointments(_=Depends(admin_only)):
    return query('''SELECT a.ApptId,u.FullName,a.DoctorName,a.Location,a.ApptTime,a.Status,a.Channel
      FROM Appointments a JOIN Users u ON u.UserId=a.UserId ORDER BY a.ApptTime DESC''')

@router.get('/users')
def list_users(search:str='',_=Depends(admin_only)):
    like=f'%{search}%'
    return query('''SELECT UserId,FullName,Email,Role,IsActive,CreatedAt,LastLoginAt FROM Users
      WHERE FullName LIKE ? OR Email LIKE ? ORDER BY CreatedAt DESC''',(like,like))

class UserPatch(BaseModel):
    role:str|None=None
    is_active:bool|None=None

@router.patch('/users/{uid}')
def patch_user(uid:int,b:UserPatch,a=Depends(admin_only)):
    if uid==a['UserId']: raise HTTPException(400,'Không thể tự đổi quyền hoặc khóa chính mình')
    if b.role in ('user','admin'): execute('UPDATE Users SET Role=? WHERE UserId=?',(b.role,uid))
    if b.is_active is not None: execute('UPDATE Users SET IsActive=? WHERE UserId=?',(int(b.is_active),uid))
    return {'message':'Đã cập nhật'}

@router.delete('/users/{uid}')
def delete_user(uid:int,a=Depends(admin_only)):
    if uid==a['UserId']: raise HTTPException(400,'Không thể xóa chính mình')
    execute('DELETE FROM Users WHERE UserId=?',(uid,))
    return {'message':'Đã xóa'}
