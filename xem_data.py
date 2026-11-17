from du_lieu import nap_csv

df, nhan, tcs = nap_csv()
print("Cột tên bệnh:", nhan)
print("Số dòng:", len(df), "| Số bệnh:", df[nhan].nunique(), "| Số triệu chứng:", len(tcs))
print("10 triệu chứng đầu:", tcs[:10])
with open("danh_sach_benh.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(df[nhan].unique())))
print("Đã ghi danh_sach_benh.txt (dùng cho bước hệ số tuổi/giới tính)")