import pandas as pd

TEN_COT_BENH = ["prognosis", "diseases", "disease", "Disease", "diseases"]

def nap_csv(path="data_en.csv"):
    cols = list(pd.read_csv(path, nrows=0).columns)
    nhan = next((c for c in TEN_COT_BENH if c in cols), cols[0])
    tcs = [c for c in cols if c != nhan]
    df = pd.read_csv(path, usecols=[nhan] + tcs)
    df[nhan] = df[nhan].astype(str).str.strip()
    for c in tcs:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype("uint8")
    return df, nhan, tcs
