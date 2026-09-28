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

def run_breakout(df, label, atr_mult=2.0, sub=None, bar_hours=None):
    """Entry: breakout dinh nen tin hieu cat len. Exit: SL uu tien, khong thi cho breakdown day nen cat xuong (khop voi backtest_main.py)."""
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
                            trades.append({'entry_dt':df['dt'].iloc[i],'r':-1.0})
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
                trades.append({'entry_dt':df['dt'].iloc[entry_i],'r':r})
                in_pos=False
                exit_pending=None
    return summarize(trades, df, label+" (Breakout - vao ngay tai dinh nen tin hieu)")

def run_pullback(df, label, atr_mult=2.0, sub=None, bar_hours=None, variant='v5'):
    """Pullback: sau khi EMA9 cat len EMA45, cho gia hoi ve EMA45 roi vao lenh khi gia pha dinh nen tin hieu.
    variant='v5' (mac dinh) - nen tin hieu la:
      * kieu "cham roi bat": nen dau tien co low <= EMA45 nhung dong cua van tren EMA45;
      * kieu "cat xuong roi cat lai": neu gia DONG CUA duoi EMA45 thi bo muc cho, doi nen dau tien dong cua
        tro lai tren EMA45. Neu da co muc cho ma gia lai dong cua duoi EMA45 truoc khi pha dinh -> doi lan cat lai tiep.
    variant='v1' (luat cu truoc 28/9/2026) - nen tin hieu la nen dau tien co low <= EMA45, muc cho co dinh.
    Exit: SL uu tien, khong thi cho breakdown day nen cat xuong (khop voi backtest_main.py)."""
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
                                    trades.append({'entry_dt':df['dt'].iloc[i],'r':-1.0})
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
                trades.append({'entry_dt':df['dt'].iloc[entry_i],'r':r})
                in_pos=False
                exit_pending=None
    return summarize(trades, df, label+" (Pullback - doi gia hoi ve EMA45 roi bat len)")

def summarize(trades, df, label):
    if not trades:
        print(f"{label}: khong co lenh nao")
        return None
    tdf = pd.DataFrame(trades)
    wins = tdf[tdf['r']>0]; losses = tdf[tdf['r']<=0]
    pf = wins['r'].sum()/abs(losses['r'].sum()) if len(losses) and losses['r'].sum()!=0 else float('inf')
    exp = tdf['r'].mean()
    cum=tdf['r'].cumsum(); peak=cum.cummax(); maxdd=(cum-peak).min()
    print(f"{label}")
    print(f"  So lenh: {len(tdf)} | Win rate: {len(wins)/len(tdf)*100:.1f}% | PF: {pf:.2f} | Expectancy: {exp:+.3f}R | Tong: {tdf['r'].sum():+.2f}R | MaxDD: {maxdd:.2f}R")
    return tdf

h1 = pd.read_csv('../data/h1_full.csv', parse_dates=['dt'])
d1 = pd.read_csv('../data/d1_full.csv', parse_dates=['dt'])
h4 = pd.read_csv('../data/h4_full.csv', parse_dates=['dt'])
CUTOFF='2025-09-30'
h1=h1[h1['dt']<=CUTOFF]; d1=d1[d1['dt']<=CUTOFF]; h4=h4[h4['dt']<=CUTOFF]
H1_GAP_HOURS = 6.0  # H1 co 7 cho thieu 1-4 nen lien tiep (max cach nhau 5h): coi la lien mach, khong cat doan/reset EMA
h1p=prep(h1,H1_GAP_HOURS); d1p=prep(d1,24.1); h4p=prep(h4,4.1)
# nen H1 (index theo dt) dung de xu ly SL trong nen vao lenh cua H4/D1
h1_sub = h1.set_index('dt')[['open','high','low','close']].sort_index()
sub_args = {'D1': dict(sub=h1_sub, bar_hours=24), 'H4': dict(sub=h1_sub, bar_hours=4), 'H1': {}}

print("="*80)
print("SO SANH: BREAKOUT (vao ngay) vs PULLBACK (doi hoi ve EMA45)")
print("="*80)
for name, dfp in [('D1', d1p), ('H4', h4p), ('H1', h1p)]:
    print(f"\n--- {name} ---")
    run_breakout(dfp, name, **sub_args[name])
    run_pullback(dfp, name, **sub_args[name])
