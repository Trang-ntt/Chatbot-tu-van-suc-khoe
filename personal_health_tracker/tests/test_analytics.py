from app.analytics import analyze_series

def test_empty():
    assert analyze_series([])["count"] == 0

def test_upward():
    result=analyze_series([1,2,3,4,5,6])
    assert result["trend"]=="tăng" and result["slope"]>0

def test_downward():
    result=analyze_series([6,5,4,3,2,1])
    assert result["trend"]=="giảm" and result["slope"]<0

def test_zscore_requires_minimum_samples():
    assert analyze_series([1,1,1,1])["outliers"]==[]
    assert 10 in analyze_series([1,1,1,1,1,1,1,1,1,1,20])["outliers"]
