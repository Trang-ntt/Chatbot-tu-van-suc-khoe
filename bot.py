import csv, re, os, math, unicodedata
from pathlib import Path
import numpy as np
from du_lieu import nap_csv
BASE=Path(__file__).resolve().parent

def norm(s):
    s=unicodedata.normalize('NFD',str(s).lower())
    s=''.join(c for c in s if unicodedata.category(c)!='Mn').replace('đ','d')
    return re.sub(r'\s+',' ',s).strip()

def nap_tu_dien():
    tc,benh={},{}
    with (BASE/'tu_dien.csv').open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            en=(r.get('en') or '').strip(); vi=(r.get('vi') or '').strip()
            if en and vi:
                (tc if r.get('loai')=='trieu_chung' else benh)[en]=vi
    return tc,benh

def nap_dong_nghia():
    d={}
    p=BASE/'dong_nghia.csv'
    if p.exists():
        with p.open(encoding='utf-8-sig',newline='') as f:
            for r in csv.DictReader(f): d[r['en'].strip()]=[x.strip() for x in r['cach_noi'].split(';') if x.strip()]
    return d

def xay_mo_hinh():
    cache=BASE/'mo_hinh.npz'
    if cache.exists():
        z=np.load(cache,allow_pickle=False)
        return z['benh'].astype(str).tolist(),z['tcs'].astype(str).tolist(),z['P']
    print('Dang xay mo hinh tu data_en.csv, lan dau co the mat vai phut...')
    df,nhan,tcs=nap_csv(BASE/'data_en.csv')
    grouped=df.groupby(nhan,sort=True)[tcs]
    tong,n=grouped.sum(),grouped.size()
    P=(tong.to_numpy(dtype=np.float64)+0.5)/(n.to_numpy(dtype=np.float64)[:,None]+1.0)
    benh=list(tong.index.astype(str))
    np.savez_compressed(cache,benh=np.array(benh,dtype=str),tcs=np.array(tcs,dtype=str),P=P)
    return benh,tcs,P

VI_TC,VI_BENH=nap_tu_dien(); DONG_NGHIA=nap_dong_nghia()
# Thông tin nhóm tuổi tham khảo được lưu riêng, không thay đổi xác suất/điểm của mô hình.
def nap_do_tuoi():
    p = BASE / 'phan_loai_do_tuoi.csv'
    if not p.exists(): return {}
    d = {}
    with p.open(encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            d[r['benh_en'].strip()] = r
    return d

DO_TUOI = nap_do_tuoi()

def nhom_tuoi(tuoi):
    if tuoi <= 5: return 'Trẻ nhỏ (0–5 tuổi)'
    if tuoi <= 12: return 'Trẻ em (6–12 tuổi)'
    if tuoi <= 17: return 'Thanh thiếu niên (13–17 tuổi)'
    if tuoi <= 39: return 'Người trưởng thành trẻ (18–39 tuổi)'
    if tuoi <= 59: return 'Trung niên (40–59 tuổi)'
    return 'Người cao tuổi (từ 60 tuổi)'

def thong_tin_tuoi(benh, tuoi, gioi=None):
    r = DO_TUOI.get(benh)
    if not r:
        return {'nhom_tuoi_thuong_gap': 'Chưa có dữ liệu tuổi đáng tin cậy',
                'phu_hop_tuoi': 'Chưa đủ dữ liệu',
                'ghi_chu_tuoi': 'Không dùng tuổi để loại trừ bệnh này.'}
    if r.get('gioi_tinh_ap_dung') == 'Nam / người có tuyến tiền liệt' and gioi == 'nu':
        return {'nhom_tuoi_thuong_gap': r['nhom_tuoi_thuong_gap'],
                'phu_hop_tuoi': 'Không áp dụng theo giới tính khai báo',
                'ghi_chu_tuoi': 'Bệnh này liên quan đến tuyến tiền liệt; không áp dụng cho người khai báo giới tính nữ.'}
    lo, hi = int(r['tuoi_min_tham_khao']), int(r['tuoi_max_tham_khao'])
    if r.get('loai_thong_tin') == 'Độ tuổi khởi phát':
        phu_hop = 'Thông tin về tuổi khởi phát, không phải giới hạn tuổi hiện tại'
    else:
        # Đối chiếu tuổi thường gặp, không phải điều kiện chẩn đoán hay loại trừ bệnh.
        hop = lo <= tuoi <= hi
        phu_hop = 'Nằm trong khoảng tuổi thường gặp' if hop else 'Ngoài khoảng tuổi thường gặp'
    return {'nhom_tuoi_thuong_gap': r['nhom_tuoi_thuong_gap'],
            'phu_hop_tuoi': phu_hop,
            'ghi_chu_tuoi': r['ghi_chu_tuoi']}

BENH,TCS,P=xay_mo_hinh(); BENH_LOWER=[norm(x) for x in BENH]
LOGP=np.log(np.clip(P,1e-9,1)); LOG1P=np.log(np.clip(1-P,1e-9,1))
# Tạo bộ nhận diện, ưu tiên cụm dài; biên từ giúp tránh nhận nhầm từ con.
CUM=[]
for i,tc in enumerate(TCS):
    forms={norm(tc),norm(VI_TC.get(tc,''))}
    forms.update(norm(x) for x in DONG_NGHIA.get(tc,[]))
    for phrase in forms:
        if phrase and len(phrase)>=2: CUM.append((phrase,i))
CUM.sort(key=lambda x:len(x[0]),reverse=True)
NEG=re.compile(r'\b(khong|ko|chua|khong bi|khong co|khong thay|khong con)\b')
RED_FLAGS=['kho tho nang','rat kho tho','khong the tho','khong noi duoc thanh cau','tim tai','bat tinh','ngat','co giat','liet nua nguoi','meo mieng dot ngot','noi kho dot ngot','dau dau du doi dot ngot','dau nguc du doi']

def trich(text):
    t=' '+norm(text)+' '; co=set();khong=set()
    for phrase,i in CUM:
        pat=r'(?<![a-z0-9])'+re.escape(phrase)+r'(?![a-z0-9])'
        for m in list(re.finditer(pat,t)):
            before=t[max(0,m.start()-28):m.start()]
            neg=bool(re.search(r'(?:\bkhong\b|\bko\b|\bchua\b)(?:\s+\w+){0,2}\s*$',before))
            (khong if neg else co).add(i)
        t=re.sub(pat,lambda m:' '*len(m.group()),t)
    co-=khong
    return co,khong

def tinh(co,khong,tuoi,gioi):
    # Không được tạo kết quả khi chưa có triệu chứng được xác nhận.
    if not co:return []
    s=np.zeros(len(BENH),dtype=np.float64)
    if co:s+=LOGP[:,sorted(co)].sum(axis=1)
    if khong:s+=LOG1P[:,sorted(khong)].sum(axis=1)
    # Tuổi/giới hiện chỉ là thông tin hội thoại; không tự áp hệ số y khoa khi CSV rỗng.
    s-=s.max(); e=np.exp(s); e/=e.sum()
    order=np.argsort(-e)[:10]
    return [(float(e[j]),int(j)) for j in order]

def cau_hoi_tiep(kq,da_hoi):
    if len(kq)<2:return None
    top=kq[:6]; w=np.array([p for p,_ in top],dtype=float)
    if w.sum()<=0:return None
    w/=w.sum(); sub=P[[j for _,j in top]]; mean=w@sub; var=w@((sub-mean)**2)
    if da_hoi:var[list(da_hoi)]=-1
    var[(mean<0.12)|(mean>0.88)]=-1
    i=int(var.argmax())
    return i if var[i]>0.008 else None

def tra_loi_co_khong(text):
    t=norm(text)
    if re.match(r'^(co|vang|dung|roi|yes|y|ok|uh)\b',t):return True
    if re.match(r'^(khong|ko|chua|no|n|hok)\b',t):return False
    return None

def phan_loai_canh_bao(text):
    # Phân biệt triệu chứng cần được đánh giá sớm với dấu hiệu cấp cứu rõ rệt.
    t=norm(text)
    # Loại các cụm bị phủ định để không cảnh báo nhầm khi người dùng nói 'không khó thở'.
    t=re.sub(r'\b(?:khong|ko|chua)\s+(?:bi\s+|co\s+)?(?:kho tho|hut hoi|dau nguc|ho ra mau|non ra mau)\b', ' ', t)
    khan_cap = (
        'kho tho nang', 'rat kho tho', 'khong the tho',
        'khong noi duoc thanh cau', 'tim tai', 'bat tinh', 'ngat',
        'co giat', 'liet nua nguoi', 'meo mieng dot ngot',
        'noi kho dot ngot', 'dau dau du doi dot ngot',
        'dau nguc du doi', 'ho ra mau nhieu'
    )
    can_danh_gia_som = ('kho tho', 'hut hoi', 'dau nguc', 'ho ra mau', 'non ra mau')
    if any(x in t for x in khan_cap): return 'khan_cap'
    if any(x in t for x in can_danh_gia_som): return 'can_danh_gia_som'
    return None

def canh_bao(co,text):
    # Tương thích với phần gọi cũ: True chỉ dành cho dấu hiệu cấp cứu rõ rệt.
    return phan_loai_canh_bao(text) == 'khan_cap'

def ten_tc(i):return VI_TC.get(TCS[i],TCS[i])
