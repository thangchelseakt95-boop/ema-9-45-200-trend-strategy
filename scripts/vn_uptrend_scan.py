"""Quét cổ phiếu Việt Nam đang uptrend theo bộ lọc EMA 9/45/200 (khung ngày).

Uptrend = EMA9 > EMA45 > EMA200 và close > EMA45.
Điểm xếp hạng = độ dốc EMA45 (20 phiên) + khoảng cách EMA9/EMA200, lọc theo thanh khoản.

Ví dụ:
    python scripts/vn_uptrend_scan.py                    # rổ VN30
    python scripts/vn_uptrend_scan.py --universe all     # HOSE + HNX
    python scripts/vn_uptrend_scan.py --symbols FPT,HPG,VCB
    python scripts/vn_uptrend_scan.py --csv-dir data/vn  # đọc <MÃ>.csv thay vì gọi API

CSV cần cột: date, open, high, low, close, volume.
Nguồn dữ liệu: VNDirect dchart (chính), TCBS (dự phòng). Cần mạng ra được 2 host này.
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

VN30 = ("ACB BCM BID BVH CTG FPT GAS GVR HDB HPG MBB MSN MWG PLX SAB SHB SSB SSI "
        "STB TCB TPB VCB VHM VIB VIC VJC VNM VPB VRE").split()  # chỉnh theo kỳ rà soát rổ mới nhất

MIN_BARS = 250  # 200 phiên làm nóng EMA200 + dư để tính độ dốc
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_vndirect(sym, start, end):
    r = requests.get("https://dchart-api.vndirect.com.vn/dchart/history", headers=HEADERS, timeout=20,
                     params={"resolution": "D", "symbol": sym, "from": start, "to": end})
    r.raise_for_status()
    j = r.json()
    if j.get("s") != "ok":
        raise ValueError(f"VNDirect: {j.get('s')}")
    # giá VNDirect tính theo nghìn đồng
    return pd.DataFrame({"date": pd.to_datetime(j["t"], unit="s"), "open": j["o"], "high": j["h"],
                         "low": j["l"], "close": j["c"], "volume": j["v"]})


def fetch_tcbs(sym, start, end):
    r = requests.get("https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-long-term", headers=HEADERS,
                     timeout=20, params={"ticker": sym, "type": "stock", "resolution": "D",
                                         "from": start, "to": end})
    r.raise_for_status()
    d = pd.DataFrame(r.json()["data"])
    d["date"] = pd.to_datetime(d["tradingDate"]).dt.tz_localize(None)
    d["close"] = d["close"] / 1000  # TCBS trả về đồng
    d["open"], d["high"], d["low"] = d["open"] / 1000, d["high"] / 1000, d["low"] / 1000
    return d[["date", "open", "high", "low", "close", "volume"]]


def load(sym, csv_dir):
    if csv_dir:
        d = pd.read_csv(Path(csv_dir) / f"{sym}.csv", parse_dates=["date"])
        return d.sort_values("date").reset_index(drop=True)
    end = int(time.time())
    start = end - 3 * 365 * 86400
    last = None
    for fn in (fetch_vndirect, fetch_tcbs):
        try:
            return fn(sym, start, end).sort_values("date").reset_index(drop=True)
        except Exception as e:  # noqa: BLE001 - thử nguồn kế tiếp
            last = e
    raise RuntimeError(f"{sym}: {last}")


def universe_all():
    r = requests.get("https://finfo-api.vndirect.com.vn/v4/stocks", headers=HEADERS, timeout=30,
                     params={"q": "type:STOCK~status:LISTED~floor:HOSE,HNX", "size": 3000, "fields": "code"})
    r.raise_for_status()
    return sorted(x["code"] for x in r.json()["data"])


def evaluate(df, min_value):
    """Trả về dict kết quả nếu mã đang uptrend, ngược lại None."""
    if len(df) < MIN_BARS:
        return None
    c = df["close"]
    e9, e45, e200 = (c.ewm(span=n, adjust=False).mean() for n in (9, 45, 200))
    last = len(df) - 1
    if not (e9.iloc[last] > e45.iloc[last] > e200.iloc[last] and c.iloc[last] > e45.iloc[last]):
        return None
    value = (c * df["volume"]).tail(20).mean() * 1000 / 1e9  # tỷ đồng/phiên (giá nghìn đồng)
    if value < min_value:
        return None
    slope = e45.iloc[last] / e45.iloc[last - 20] - 1
    spread = e9.iloc[last] / e200.iloc[last] - 1
    # số phiên liên tiếp giữ cấu trúc uptrend
    ok = (e9 > e45) & (e45 > e200) & (c > e45)
    run = int(np.argmin(ok.values[::-1])) if not ok.all() else len(ok)
    return {"close": round(c.iloc[last], 2), "GTGD_ty": round(value, 1), "slope45_20p_%": round(slope * 100, 1),
            "e9_vs_e200_%": round(spread * 100, 1), "phien_uptrend": run,
            "cach_e45_%": round((c.iloc[last] / e45.iloc[last] - 1) * 100, 1),
            "score": round(slope * 100 + spread * 50, 1), "ngay": df["date"].iloc[last].date()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--universe", choices=["vn30", "all"], default="vn30")
    ap.add_argument("--symbols", help="danh sách mã, phân cách bằng dấu phẩy (ghi đè --universe)")
    ap.add_argument("--csv-dir", help="thư mục chứa <MÃ>.csv thay vì gọi API")
    ap.add_argument("--min-value", type=float, default=10.0, help="GTGD trung bình 20 phiên tối thiểu (tỷ đồng)")
    ap.add_argument("--top", type=int, default=30)
    a = ap.parse_args()

    if a.symbols:
        syms = [s.strip().upper() for s in a.symbols.split(",") if s.strip()]
    elif a.csv_dir:
        syms = sorted(p.stem for p in Path(a.csv_dir).glob("*.csv"))
    elif a.universe == "all":
        syms = universe_all()
    else:
        syms = VN30

    rows, errors = [], []
    for s in syms:
        try:
            res = evaluate(load(s, a.csv_dir), a.min_value)
        except Exception as e:  # noqa: BLE001
            errors.append(str(e))
            continue
        if res:
            rows.append({"ma": s, **res})
        if not a.csv_dir:
            time.sleep(0.15)

    print(f"Đã quét {len(syms) - len(errors)}/{len(syms)} mã, {len(rows)} mã đang uptrend.")
    if rows:
        out = pd.DataFrame(rows).sort_values("score", ascending=False).head(a.top)
        print(out.to_string(index=False))
    if errors:
        print(f"\n{len(errors)} mã lỗi, ví dụ: {errors[0]}", file=sys.stderr)
        if len(errors) == len(syms):
            sys.exit(1)


if __name__ == "__main__":
    main()
