import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from auth import current_user
from database import query, execute
from services.symptom_engine import analyze, DATA

router = APIRouter(prefix='/api/symptoms', tags=['Symptoms'])

class SymptomIn(BaseModel):
    symptoms: list[str] = Field(min_length=1)
    severity: int = Field(default=1, ge=1, le=3)
    days_since: int | None = Field(default=None, ge=0)

@router.get('/list')
def symptom_list(u=Depends(current_user)):
    names = sorted({s for d in DATA for s in d['symptoms']})
    return {'symptoms': names}

@router.post('/analyze')
def symptom_analyze(b: SymptomIn, u=Depends(current_user)):
    results = analyze(b.symptoms)
    payload = {'symptoms': b.symptoms, 'results': results}
    execute('INSERT INTO SymptomChecks(UserId,SymptomText,Severity,DaysSince,ResultJson) VALUES(?,?,?,?,?)',
            (u['UserId'], ', '.join(b.symptoms), b.severity, b.days_since, json.dumps(payload, ensure_ascii=False)))
    return payload

@router.get('/mine')
def symptom_history(u=Depends(current_user)):
    return query('SELECT CheckId,SymptomText,Severity,DaysSince,ResultJson,CreatedAt FROM SymptomChecks WHERE UserId=? ORDER BY CreatedAt DESC', (u['UserId'],))
