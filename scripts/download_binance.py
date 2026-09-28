"""Tai nen tu Binance API (public, khong can API key) va luu CSV: dt,open,high,low,close,volume.
Chi giu nen DA DONG (close_time < thoi diem tai), bo nen dang chay do o cuoi.

Cach dung:  python download_binance.py PAXGUSDT 1h ../data/paxg_h1.csv
            python download_binance.py PAXGUSDT 4h ../data/paxg_h4.csv
"""
import sys, time, json, urllib.request
import pandas as pd

START = '2021-01-01'
URL = 'https://api.binance.com/api/v3/klines?symbol={s}&interval={i}&startTime={t}&limit=1000'

def fetch(symbol, interval, start=START):
    t = int(pd.Timestamp(start).timestamp()*1000)
    now_ms = int(time.time()*1000)
    rows = []
    while True:
        with urllib.request.urlopen(URL.format(s=symbol, i=interval, t=t), timeout=30) as r:
            batch = json.loads(r.read())
        if not batch:
            break
        rows += batch
        t = batch[-1][0] + 1
        if len(batch) < 1000:
            break
        time.sleep(0.2)
    df = pd.DataFrame(rows, columns=['open_time','open','high','low','close','volume','close_time',
                                     'qv','n','tbv','tqv','ig'])
    df = df[df['close_time'] < now_ms]  # bo nen chua dong
    out = pd.DataFrame({'dt': pd.to_datetime(df['open_time'], unit='ms')})
    for c in ['open','high','low','close','volume']:
        out[c] = df[c].astype(float).values
    return out.drop_duplicates('dt').sort_values('dt').reset_index(drop=True)

if __name__ == '__main__':
    symbol, interval, path = sys.argv[1], sys.argv[2], sys.argv[3]
    df = fetch(symbol, interval)
    df.to_csv(path, index=False)
    print(f"{symbol} {interval}: {len(df)} nen, {df['dt'].min()} -> {df['dt'].max()} -> {path}")
