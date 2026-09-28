"""Out-of-sample validation: warm-up EMA/ATR tren du lieu tu 2025-01-01,
nhung chi tinh thong ke cho cac lenh VAO sau 30/9/2025 (ngoai mau so voi
bang ket qua chinh trong README, von dung du lieu 2021-01-01 -> 2025-09-30).

Du lieu lay truc tiep tu Binance API (data/h1_oos_binance.csv, h4_oos_binance.csv)
vi h1_full.csv/h4_full.csv trong repo khong du lieu lien tuc sau moc do."""
import pandas as pd
import numpy as np

WARMUP_BARS = 200  # EMA200 khoi tao tu nen dau -> can ~200 nen (trong so gia tri khoi tao con ~13%) truoc khi tin tin hieu

def prep(df, gap_thresh_hours):
    df = df[['dt','open','high','low','close']].copy()
    df = df.sort_values('dt').drop_duplicates('dt').reset_index(drop=True)
    df['gap_hours'] = df['dt'].diff().dt.total_seconds()/3600
    df['seg'] = (df['gap_hours'] > gap_thresh_hours).cumsum()

    def ci(g):
        g = g.copy()
        g['EMA9'] = g['close'].ewm(span=9, adjust=False).mean()
        g['EMA45'] = g['close'].ewm(span=45, adjust=False).mean()
        g['EMA200'] = g['close'].ewm(span=200, adjust=False).mean()
        prev_close = g['close'].shift(1)
        tr = pd.concat([g['high']-g['low'], (g['high']-prev_close).abs(), (g['low']-prev_close).abs()], axis=1).max(axis=1)
        g['ATR14'] = tr.ewm(span=14, adjust=False).mean()
        g['emaup'] = g['EMA9'] > g['EMA45']
        sh = g['emaup'].shift(1, fill_value=False)
        g['cross_up'] = g['emaup'] & (~sh)
        g['cross_down'] = (~g['emaup']) & sh
        g['above200'] = g['close'] > g['EMA200']
        g['aligned'] = (g['EMA9'] > g['EMA45']) & (g['EMA45'] > g['EMA200'])
        # lam nong EMA: WARMUP_BARS nen dau cua moi doan chi dung de tinh EMA/ATR, khong duoc vao lenh
        g['aligned'] &= (np.arange(len(g)) >= WARMUP_BARS)
        return g

    df = df.groupby('seg', group_keys=False).apply(ci).reset_index(drop=True)
    df['gap_hours'] = df['dt'].diff().dt.total_seconds()/3600
    df['seg'] = (df['gap_hours'] > gap_thresh_hours).cumsum()
    return df

def stop_in_entry_bar(row, pending, sl, sub=None, bar_hours=None):
    """Nen vao lenh co cham SL sau khi khop khong? Neu co du lieu nen nho hon (sub, vd H1 cho H4/D1)
    thi duyet tung nen con theo thu tu thoi gian: tim nen con dau tien pha muc cho, roi xem tu nen do
    tro di co nen nao cham SL. Neu khong co du lieu nen con -> gia dinh bat loi (cham SL la thua)."""
    if sub is not None:
        s = sub.loc[row['dt'] : row['dt'] + pd.Timedelta(hours=bar_hours) - pd.Timedelta(seconds=1)]
        filled = False
        for h in s.itertuples():
            if not filled and h.high > pending:
                filled = True
            if filled and h.low <= sl:
                return True
        if filled:
            return False
    return row['low'] <= sl

def run_backtest_atr(df, atr_mult=2.0, sub=None, bar_hours=None):
    """Entry: breakout dinh nen tin hieu cat len. Exit: SL uu tien, khong thi cho breakdown day nen cat xuong."""
    in_pos=False; entry=None; sl=None; pending=None; entry_i=None; risk=None
    exit_pending=None
    trades=[]
    for i in range(1, len(df)):
        row = df.iloc[i]; prev = df.iloc[i-1]
        if not in_pos:
            if pending is not None and prev['cross_down']:
                pending = None  # EMA9 cat xuong EMA45 truoc khi breakout -> huy lenh cho mua
            # dat lenh cho TRUOC khi kiem tra khop -> nen ngay sau nen tin hieu cung duoc xet breakout
            if prev['cross_up'] and prev['aligned']:
                pending = prev['high']
            if pending is not None:
                if row['high'] > pending and prev['aligned']:
                    entry = max(pending, row['open'])  # gap mo cua tren muc cho -> khop o gia mo cua
                    sl = entry - atr_mult*prev['ATR14']
                    if entry > sl:
                        in_pos = True; entry_i = i; risk = entry - sl
                        if stop_in_entry_bar(row, pending, sl, sub, bar_hours):  # cham SL ngay trong nen vao lenh (dung nen H1 neu co)
                            trades.append({'entry_dt':row['dt'],'exit_dt':row['dt'],'entry':round(entry,2),'sl':round(sl,2),'exit':round(sl,2),'r':-1.0})
                            in_pos = False
                    pending = None
            exit_pending = None
        else:
            exit_p=None
            if exit_pending is not None and prev['cross_up']:
                exit_pending = None  # EMA9 cat len lai truoc khi breakdown -> huy lenh cho thoat
            if prev['cross_down']:
                exit_pending = prev['low']
            if row['low'] <= sl:
                exit_p = min(sl, row['open'])  # gap mo cua duoi SL -> thoat o gia mo cua
            elif exit_pending is not None and row['low'] < exit_pending:
                exit_p = min(exit_pending, row['open'])
            if exit_p is not None:
                r = (exit_p - entry)/risk
                trades.append({'entry_dt':df['dt'].iloc[entry_i],'exit_dt':df['dt'].iloc[i],'entry':round(entry,2),'sl':round(sl,2),'exit':round(exit_p,2),'r':round(r,3)})
                in_pos=False
                exit_pending=None
    return pd.DataFrame(trades)

def summarize_oos(tdf, label, oos_start):
    oos = tdf[tdf['entry_dt'] >= oos_start]
    if oos.empty:
        print(f"{label}: khong co lenh nao vao sau {oos_start.date()}")
        return
    wins = oos[oos['r']>0]; losses = oos[oos['r']<=0]
    pf = wins['r'].sum()/abs(losses['r'].sum()) if len(losses) and losses['r'].sum()!=0 else float('inf')
    print(f"{label}: n={len(oos)} | WR={len(wins)/len(oos)*100:.1f}% | PF={pf:.2f} | Expectancy={oos['r'].mean():+.3f}R | TongR={oos['r'].sum():+.2f}R")

OOS_START = pd.Timestamp('2025-10-01')

h1 = pd.read_csv('../data/h1_oos_binance.csv')
h1['dt'] = pd.to_datetime(h1['open_time'], unit='ms')
h4 = pd.read_csv('../data/h4_oos_binance.csv')
h4['dt'] = pd.to_datetime(h4['open_time'], unit='ms')
for c in ['open','high','low','close']:
    h1[c] = h1[c].astype(float)
    h4[c] = h4[c].astype(float)

d1_raw = h1.set_index('dt')[['open','high','low','close']].resample('1D').agg(
    {'open':'first','high':'max','low':'min','close':'last'}).dropna().reset_index()
if h1['dt'].max().hour != 23:  # ngay cuoi chua du 24 nen H1 -> bo ngay do khoi D1
    d1_raw = d1_raw[d1_raw['dt'] < h1['dt'].max().normalize()].reset_index(drop=True)

H1_GAP_HOURS = 6.0  # H1 co 7 cho thieu 1-4 nen lien tiep (max cach nhau 5h): coi la lien mach, khong cat doan/reset EMA
h1p = prep(h1[['dt','open','high','low','close']], H1_GAP_HOURS)
h4p = prep(h4[['dt','open','high','low','close']], 4.1)
d1p = prep(d1_raw, 24.1)
# nen H1 (index theo dt) dung de xu ly SL trong nen vao lenh cua H4/D1
h1_sub = h1.set_index('dt')[['open','high','low','close']].sort_index()

print("="*90)
print(f"OUT-OF-SAMPLE VALIDATION: warm-up tu {h1['dt'].min().date()}, chi tinh lenh vao sau {OOS_START.date()}")
print("="*90)

summarize_oos(run_backtest_atr(d1p, atr_mult=3.0, sub=h1_sub, bar_hours=24), "D1  ATR=3.0x (cau hinh toi uu in-sample)", OOS_START)
print()
summarize_oos(run_backtest_atr(h4p, atr_mult=2.0, sub=h1_sub, bar_hours=4), "H4  ATR=2.0x (cau hinh toi uu in-sample)", OOS_START)
print()
for mult in [1.5, 2.0, 2.5, 3.0]:
    summarize_oos(run_backtest_atr(h1p, atr_mult=mult), f"H1  ATR={mult}x", OOS_START)
