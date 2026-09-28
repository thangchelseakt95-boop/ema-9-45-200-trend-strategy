"""Backtest chien luoc EMA9/EMA45 (Breakout + Pullback) cho mot tai san bat ky tu file CSV nen H1/H4.
Dung lai nguyen ham prep/stop_in_entry_bar/run_breakout/run_pullback cua oos_pullback_test.py (chi them
gia vao/SL/ra vao moi lenh de tinh phi, khong doi logic). D1 = resample tu H1.

Cach dung:  python asset_test.py ../data/paxg_h1.csv ../data/paxg_h4.csv PAXG
Tach giai doan: lenh vao truoc 1/10/2025 = in-sample, tu 1/10/2025 = ngoai mau (cung moc voi BTC).
"""
import sys
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
        pc = g['close'].shift(1)
        tr = pd.concat([g['high']-g['low'], (g['high']-pc).abs(), (g['low']-pc).abs()], axis=1).max(axis=1)
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

def run_breakout(df, atr_mult=2.0, sub=None, bar_hours=None):
    """Entry: breakout dinh nen tin hieu cat len. Exit: SL uu tien, khong thi cho breakdown day nen cat xuong."""
    in_pos=False; entry=None; sl=None; pending=None; risk=None; entry_i=None
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
                    entry = max(pending, row['open']); sl = entry - atr_mult*prev['ATR14']
                    if entry > sl:
                        in_pos=True; entry_i=i; risk=entry-sl
                        if stop_in_entry_bar(row, pending, sl, sub, bar_hours):  # cham SL ngay trong nen vao lenh (dung nen H1 neu co)
                            trades.append({'entry_dt':df['dt'].iloc[i],'entry':entry,'sl':sl,'exit':sl,'r':-1.0})
                            in_pos=False
                    pending=None
            exit_pending = None
        else:
            exit_p=None
            if exit_pending is not None and prev['cross_up']:
                exit_pending = None  # EMA9 cat len lai truoc khi breakdown -> huy lenh cho thoat
            if prev['cross_down']:
                exit_pending = prev['low']
            if row['low']<=sl:
                exit_p = min(sl, row['open'])  # gap mo cua duoi SL -> thoat o gia mo cua
            elif exit_pending is not None and row['low'] < exit_pending:
                exit_p = min(exit_pending, row['open'])
            if exit_p is not None:
                r=(exit_p-entry)/risk
                trades.append({'entry_dt':df['dt'].iloc[entry_i],'entry':entry,'sl':sl,'exit':exit_p,'r':r})
                in_pos=False
                exit_pending=None
    return pd.DataFrame(trades)

def run_pullback(df, atr_mult=2.0, sub=None, bar_hours=None, variant='v5'):
    """Pullback: sau khi EMA9 cat len EMA45, cho gia hoi ve EMA45 roi vao lenh khi gia pha dinh nen tin hieu.
    variant='v5' (mac dinh) - nen tin hieu la:
      * kieu "cham roi bat": nen dau tien co low <= EMA45 nhung dong cua van tren EMA45;
      * kieu "cat xuong roi cat lai": neu gia DONG CUA duoi EMA45 thi bo muc cho, doi nen dau tien dong cua
        tro lai tren EMA45. Neu da co muc cho ma gia lai dong cua duoi EMA45 truoc khi pha dinh -> doi lan cat lai tiep.
    variant='v1' (luat cu truoc 28/9/2026) - nen tin hieu la nen dau tien co low <= EMA45, muc cho co dinh.
    Exit: SL uu tien, khong thi cho breakdown day nen cat xuong."""
    in_pos=False; entry=None; sl=None; risk=None; entry_i=None
    waiting=False; pullback_pending=None; below=False
    exit_pending=None
    trades=[]
    for i in range(1, len(df)):
        row = df.iloc[i]; prev = df.iloc[i-1]
        if not in_pos:
            # bat dau cho pullback TRUOC khi xet nen hien tai -> nen ngay sau nen tin hieu cung duoc xet
            if prev['cross_up'] and prev['aligned']:
                waiting = True
                pullback_pending = None; below = False
            if waiting:
                if prev['cross_down']:
                    waiting=False; pullback_pending=None; below=False
                else:
                    if pullback_pending is not None:
                        # dieu kien loc dung nen truoc (da dong cua), tranh nhin truoc gia dong cua nen hien tai
                        if row['high'] > pullback_pending and prev['aligned'] and prev['emaup']:
                            entry = max(pullback_pending, row['open']); sl = entry - atr_mult*prev['ATR14']
                            if entry > sl:
                                in_pos=True; entry_i=i; risk=entry-sl
                                if stop_in_entry_bar(row, pullback_pending, sl, sub, bar_hours):  # cham SL ngay trong nen vao lenh (dung nen H1 neu co)
                                    trades.append({'entry_dt':df['dt'].iloc[i],'entry':entry,'sl':sl,'exit':sl,'r':-1.0})
                                    in_pos=False
                            waiting=False; pullback_pending=None; below=False
                    if not in_pos and waiting:
                        if variant == 'v5' and row['close'] < row['EMA45']:
                            below = True; pullback_pending = None  # dong cua duoi EMA45 -> bo muc cho, doi nen cat len lai
                        elif variant == 'v5' and below and row['close'] > row['EMA45'] and row['emaup'] and row['aligned']:
                            pullback_pending = row['high']; below = False  # nen dau tien dong cua tro lai tren EMA45
                        elif not below and pullback_pending is None and row['low'] <= row['EMA45'] and row['emaup'] and row['aligned']:
                            pullback_pending = row['high']  # nen cham EMA45 (v5: dong cua van tren EMA45)
            exit_pending = None
        else:
            exit_p=None
            if exit_pending is not None and prev['cross_up']:
                exit_pending = None  # EMA9 cat len lai truoc khi breakdown -> huy lenh cho thoat
            if prev['cross_down']:
                exit_pending = prev['low']
            if row['low']<=sl:
                exit_p = min(sl, row['open'])  # gap mo cua duoi SL -> thoat o gia mo cua
            elif exit_pending is not None and row['low'] < exit_pending:
                exit_p = min(exit_pending, row['open'])
            if exit_p is not None:
                r=(exit_p-entry)/risk
                trades.append({'entry_dt':df['dt'].iloc[entry_i],'entry':entry,'sl':sl,'exit':exit_p,'r':r})
                in_pos=False
                exit_pending=None
    return pd.DataFrame(trades)

IS_END = pd.Timestamp('2025-10-01')
FEES = [0.0004, 0.001]  # 0.04%/chieu (taker futures) va 0.1%/chieu (spot)
BO_MULTS = [1.0,1.5,2.0,2.5,3.0,3.5,4.0]
PB_MULTS = [1.5,2.0,2.5,3.0]
H1_GAP_HOURS = 6.0  # 7 cho thieu 1-4 nen H1 do Binance bao tri (trung ngay voi BTC)

def stats(t, fee=0.0):
    if t is None or len(t) == 0:
        return None
    r = t['r'] - fee*(t['entry']+t['exit'])/(t['entry']-t['sl'])
    w = r[r>0]; l = r[r<=0]
    pf = w.sum()/abs(l.sum()) if len(l) and l.sum()!=0 else float('inf')
    c = pd.concat([pd.Series([0.0]), r.cumsum()], ignore_index=True); dd = (c-c.cummax()).min()
    return {'lenh': len(r), 'winrate': len(w)/len(r)*100, 'pf': pf, 'expectancy': r.mean(),
            'tong_r': r.sum(), 'max_dd': dd, 'r_dd': r.sum()/abs(dd) if dd < 0 else float('inf')}

h1_path, h4_path, name = sys.argv[1], sys.argv[2], sys.argv[3]
h1 = pd.read_csv(h1_path, parse_dates=['dt'])
h4 = pd.read_csv(h4_path, parse_dates=['dt'])
d1_raw = h1.set_index('dt')[['open','high','low','close']].resample('1D').agg(
    {'open':'first','high':'max','low':'min','close':'last'}).dropna().reset_index()
if h1['dt'].max().hour != 23:  # ngay cuoi chua du 24 nen H1
    d1_raw = d1_raw[d1_raw['dt'] < h1['dt'].max().normalize()].reset_index(drop=True)
h1_sub = h1.set_index('dt')[['open','high','low','close']].sort_index()
frames = {'D1': prep(d1_raw, 24.1), 'H4': prep(h4, 4.1), 'H1': prep(h1, H1_GAP_HOURS)}
sub_args = {'D1': dict(sub=h1_sub, bar_hours=24), 'H4': dict(sub=h1_sub, bar_hours=4), 'H1': {}}

rows = []
for tf, dfp in frames.items():
    print(f"\n{'='*112}\n{name} {tf}: {dfp['dt'].iloc[0].date()} -> {dfp['dt'].iloc[-1].date()}  ({len(dfp)} nen, {dfp['seg'].nunique()} doan)\n{'='*112}")
    print(f"{'':>13} | {'IN-SAMPLE (truoc 10/2025, chua phi)':^38} | {'NGOAI MAU':^22} | {'TOAN BO, PHI 0.04%':^30} | {'PHI 0.1%':^12}")
    print(f"{'':>13} | {'Lenh':>4} {'Win':>6} {'PF':>5} {'Expect':>8} {'MaxDD':>7} | {'Lenh':>4} {'PF':>5} {'Tong R':>8} | {'Lenh':>4} {'PF':>5} {'Expect':>8} {'MaxDD':>7} | {'PF':>5} {'R/DD':>5}")
    for strat, fn, mults in [('Breakout', run_breakout, BO_MULTS), ('Pullback', run_pullback, PB_MULTS)]:
        for m in mults:
            t = fn(dfp, atr_mult=m, **sub_args[tf])
            ti = t[t['entry_dt'] < IS_END] if len(t) else t
            to = t[t['entry_dt'] >= IS_END] if len(t) else t
            a = stats(ti); b = stats(to); f = stats(t, FEES[0]); g = stats(t, FEES[1])
            rows.append({'tai_san': name, 'khung': tf, 'chien_luoc': strat, 'atr': m,
                         **{'is_'+k: v for k, v in (a or {}).items()}, **{'oos_'+k: v for k, v in (b or {}).items()},
                         **{'full_phi004_'+k: v for k, v in (f or {}).items()}, **{'full_phi01_'+k: v for k, v in (g or {}).items()}})
            sa = f"{a['lenh']:>4} {a['winrate']:>5.1f}% {a['pf']:>5.2f} {a['expectancy']:>+7.3f}R {a['max_dd']:>6.2f}R" if a else f"{'0':>4} {'':>32}"
            sb = f"{b['lenh']:>4} {b['pf']:>5.2f} {b['tong_r']:>+7.2f}R" if b else f"{'0':>4} {'-':>5} {'-':>8}"
            sf = f"{f['lenh']:>4} {f['pf']:>5.2f} {f['expectancy']:>+7.3f}R {f['max_dd']:>6.2f}R" if f else f"{'0':>4}"
            sg = f"{g['pf']:>5.2f} {g['r_dd']:>5.2f}" if g else ''
            print(f"{strat:>8} {m:.1f}x | {sa} | {sb} | {sf} | {sg}")

out = f"../results/{name.lower()}_summary.csv"
pd.DataFrame(rows).round(3).to_csv(out, index=False)
p0, p1 = h1['close'].iloc[0], h1['close'].iloc[-1]
c = h1['close'].values; bh_dd = ((c-np.maximum.accumulate(c))/np.maximum.accumulate(c)).min()*100
print(f"\nBuy & Hold {name}: {p0:,.2f} -> {p1:,.2f} (x{p1/p0:.2f}), Max DD {bh_dd:.1f}%")
print(f"Da luu: {out}")
