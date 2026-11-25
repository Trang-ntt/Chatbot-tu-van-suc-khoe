"""Explainable trend calculations; outputs are informational, not diagnoses."""
from math import sqrt
from statistics import mean, pstdev


def analyze_series(values: list[float]) -> dict:
    clean = [float(v) for v in values if v is not None]
    if not clean:
        return {"count": 0, "moving_average": [], "slope": 0.0,
                "trend": "chưa đủ dữ liệu", "z_scores": [], "outliers": [],
                "explanation": "Chưa có dữ liệu để phân tích."}
    window = min(3, len(clean))
    moving = [round(mean(clean[max(0, i-window+1):i+1]), 2) for i in range(len(clean))]
    # OLS slope with equally spaced observations; unit is value per observation.
    xs = list(range(len(clean)))
    xbar, ybar = mean(xs), mean(clean)
    denom = sum((x-xbar)**2 for x in xs)
    slope = sum((x-xbar)*(y-ybar) for x, y in zip(xs, clean)) / denom if denom else 0.0
    if len(clean) < 3:
        trend = "chưa đủ dữ liệu"
    elif slope > max(abs(ybar) * 0.01, 0.01):
        trend = "tăng"
    elif slope < -max(abs(ybar) * 0.01, 0.01):
        trend = "giảm"
    else:
        trend = "tương đối ổn định"
    sd = pstdev(clean) if len(clean) > 1 else 0.0
    z = [round((v-ybar)/sd, 2) if sd else 0.0 for v in clean]
    outliers = [i for i, score in enumerate(z) if len(clean) >= 5 and abs(score) >= 2.5]
    advice = {
        "tăng": "Chỉ số có xu hướng tăng trong các lần ghi nhận. Hãy tiếp tục đo đúng cách, theo dõi cùng điều kiện và trao đổi với nhân viên y tế nếu xu hướng kéo dài.",
        "giảm": "Chỉ số có xu hướng giảm trong các lần ghi nhận. Hãy theo dõi thêm và đối chiếu với mục tiêu cá nhân đã được chuyên môn tư vấn.",
        "tương đối ổn định": "Chỉ số tương đối ổn định trong dữ liệu hiện có. Tiếp tục ghi nhận đều đặn.",
        "chưa đủ dữ liệu": "Cần thêm các lần đo được ghi nhận đều đặn để đánh giá xu hướng."
    }[trend]
    return {"count": len(clean), "moving_average": moving, "slope": round(slope, 4),
            "trend": trend, "z_scores": z, "outliers": outliers,
            "explanation": advice,
            "method": "Trung bình trượt tối đa 3 mẫu, hồi quy tuyến tính OLS và Z-score (chỉ đánh dấu khi có ít nhất 5 mẫu).",
            "disclaimer": "Kết quả thống kê tham khảo, không phải chẩn đoán hoặc lời khuyên điều trị."}
