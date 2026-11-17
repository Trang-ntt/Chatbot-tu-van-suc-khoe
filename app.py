from flask import Flask,render_template,request,jsonify
from pathlib import Path
import uuid, threading
import bot
BASE=Path(__file__).resolve().parent
app=Flask(__name__,template_folder=str(BASE/'templates'),static_folder=str(BASE/'static'))
app.secret_key='doi-chuoi-bi-mat-khi-trien-khai'
PHIEN={}; KHOA=threading.Lock(); GIOI_TINH_HOP_LE=('nam','nu'); SO_CAU_HOI_TOI_DA=5

def tao_phien(tuoi,gioi):
    ma=str(uuid.uuid4())
    with KHOA: PHIEN[ma]={'tuoi':tuoi,'gioi':gioi,'co':set(),'khong':set(),'da_hoi':set(),'so_cau_hoi':0,'cau_hoi_dang_cho':None,'canh_bao':False}
    return ma

def lay_ket_qua(p):return bot.tinh(p['co'],p['khong'],p['tuoi'],p['gioi'])
def tao_ket_qua(p):
    kq=lay_ket_qua(p); ds=[]
    for diem,j in kq[:5]:
        ds.append({'ten':bot.VI_BENH.get(bot.BENH[j],bot.BENH[j]),'ten_goc':bot.BENH[j],'diem':round(diem*100,2)})
    return {'loai':'ket_qua','trieu_chung_co':[bot.ten_tc(i) for i in sorted(p['co'])], 'trieu_chung_khong':[bot.ten_tc(i) for i in sorted(p['khong'])], 'danh_sach_benh':ds,'canh_bao':p['canh_bao'],'loi_khuyen':'Điểm là mức độ phù hợp tương đối trong nhóm bệnh của mô hình, không phải xác suất mắc bệnh thực tế hay chẩn đoán. Hãy liên hệ cơ sở y tế để được thăm khám.'}
def tiep_tuc(p):
    kq=lay_ket_qua(p);p['da_hoi'].update(p['co']|p['khong'])
    if p['so_cau_hoi']>=SO_CAU_HOI_TOI_DA:return tao_ket_qua(p)
    i=bot.cau_hoi_tiep(kq,p['da_hoi'])
    if i is None:return tao_ket_qua(p)
    p['da_hoi'].add(i);p['cau_hoi_dang_cho']=i;p['so_cau_hoi']+=1
    return {'loai':'cau_hoi','tin_nhan':f"Bạn có gặp triệu chứng '{bot.ten_tc(i)}' không?"}
def xu_ly(p,text):
    co,khong=bot.trich(text)
    p['co'].update(co);p['khong'].update(khong);p['co']-=p['khong']
    if bot.canh_bao(p['co'],text):p['canh_bao']=True
    if not p['co'] and not p['khong']:
        return {'loai':'chua_hieu','tin_nhan':"Mình chưa nhận diện được triệu chứng. Bạn thử viết ngắn gọn như: sốt, ho, đau họng, nghẹt mũi hoặc khó thở nhé."}
    return tiep_tuc(p)
@app.get('/')
def home():return render_template('index.html')
@app.get('/api/health')
def health():return jsonify({'status':'ok','so_benh':len(bot.BENH),'so_trieu_chung':len(bot.TCS)})
@app.post('/api/bat-dau')
def bat_dau():
    d=request.get_json(silent=True) or {}
    try:tuoi=int(d.get('tuoi'))
    except (TypeError,ValueError):return jsonify({'loi':'Bạn hãy nhập tuổi bằng số.'}),400
    gioi=str(d.get('gioi','')).strip().lower()
    if not 1<=tuoi<=119:return jsonify({'loi':'Tuổi phải từ 1 đến 119.'}),400
    if gioi not in GIOI_TINH_HOP_LE:return jsonify({'loi':'Hãy chọn giới tính nam hoặc nữ.'}),400
    ma=tao_phien(tuoi,gioi)
    return jsonify({'ma_phien':ma,'tin_nhan':'Mình đã sẵn sàng. Bạn hãy mô tả triệu chứng đang gặp phải nhé.'})
@app.post('/api/tin-nhan')
def tin_nhan():
    d=request.get_json(silent=True) or {};ma=d.get('ma_phien');text=str(d.get('noi_dung','')).strip()
    if ma not in PHIEN:return jsonify({'loi':'Phiên trò chuyện không tồn tại. Hãy bắt đầu lại.'}),400
    if not text:return jsonify({'loi':'Bạn hãy nhập nội dung trước khi gửi.'}),400
    p=PHIEN[ma];i=p['cau_hoi_dang_cho']
    if i is not None:
        answer=bot.tra_loi_co_khong(text)
        if answer is not None:
            (p['co'] if answer else p['khong']).add(i)
            (p['khong'] if answer else p['co']).discard(i)
            p['cau_hoi_dang_cho']=None;result=tiep_tuc(p)
        else:p['cau_hoi_dang_cho']=None;result=xu_ly(p,text)
    else:result=xu_ly(p,text)
    return jsonify(result)
@app.post('/api/lam-moi')
def lam_moi():
    d=request.get_json(silent=True) or {};PHIEN.pop(d.get('ma_phien'),None);return jsonify({'thanh_cong':True})
if __name__=='__main__':app.run(host='127.0.0.1',port=5000,debug=False)
