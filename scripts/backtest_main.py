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

def run_backtest_atr(df, label, atr_mult=2.0, sub=None, bar_hours=None):
    """Entry: gia pha vo (breakout) dinh nen tin hieu cat len, dieu kien EMA9>EMA45>EMA200 (aligned).
    Exit: SL uu tien truoc; neu khong thi cho gia pha vo (breakdown) day cua nen tin hieu cat xuong roi moi thoat."""
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
                        in_pos = True
                        entry_i = i
                        risk = entry - sl
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
                trades.append({'entry_dt':df['dt'].iloc[entry_i],'exit_dt':row['dt'],'entry':round(entry,2),'sl':round(sl,2),'exit':round(exit_p,2),'r':round(r,3)})
                in_pos=False
                exit_pending=None

    tdf = pd.DataFrame(trades)
    wins = tdf[tdf['r']>0]
    losses = tdf[tdf['r']<=0]
    pf = wins['r'].sum() / abs(losses['r'].sum()) if len(losses) and losses['r'].sum()!=0 else float('inf')
    expectancy = tdf['r'].mean()
    cum = tdf['r'].cumsum()
    peak = cum.cummax()
    maxdd = (cum-peak).min()
    years = (df['dt'].iloc[-1]-df['dt'].iloc[0]).days/365.25

    print(f"\n{'='*72}\n{label} (bo qua WARMUP_BARS nen dau, chi dung de lam nong EMA)\n{'='*72}")
    print(f"Du lieu: {df['dt'].iloc[0].date()} -> {df['dt'].iloc[-1].date()}  (~{years:.2f} nam, {len(df)} nen, {df['seg'].nunique()} doan)")
    print(f"Tong so lenh: {len(tdf)}  |  Lenh/nam: {len(tdf)/years:.1f}")
    print(f"Win rate: {len(wins)/len(tdf)*100:.1f}%  ({len(wins)} thang / {len(losses)} thua)")
    print(f"Profit Factor: {pf:.2f}")
    print(f"Expectancy: {expectancy:+.3f}R/lenh")
    print(f"Tong R tich luy: {tdf['r'].sum():+.2f}R")
    print(f"TB lenh thang: {wins['r'].mean():+.2f}R   |  TB lenh thua: {losses['r'].mean():+.2f}R")
    print(f"Lenh thang lon nhat: {wins['r'].max():+.2f}R   |  Lenh thua nang nhat: {losses['r'].min():+.2f}R")
    print(f"Max Drawdown: {maxdd:.2f}R")
    return tdf

def run_hybrid(df, label, atr_mult=2.0, risk_pct=0.01, fee=0.0004, sub=None, bar_hours=None):
    start_price = df['close'].iloc[0]
    end_price = df['close'].iloc[-1]
    core_btc = 1.0
    satellite_cash = 0.0
    in_pos=False; entry=None; sl=None; pending=None; risk=None; qty=None
    exit_pending=None
    trades=[]
    curve=[core_btc*start_price]
    for i in range(1, len(df)):
        row = df.iloc[i]; prev = df.iloc[i-1]
        account_value = core_btc*row['close'] + satellite_cash
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
                    risk = entry - sl
                    if risk > 0:
                        qty = (account_value*risk_pct)/risk
                        in_pos = True
                        if stop_in_entry_bar(row, pending, sl, sub, bar_hours):  # cham SL ngay trong nen vao lenh (dung nen H1 neu co)
                            pnl = qty*(sl-entry) - qty*entry*fee - qty*sl*fee
                            satellite_cash += pnl
                            trades.append({'dt':row['dt'],'r':-1.0,'pnl':pnl})
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
                pnl = qty*(exit_p-entry) - qty*entry*fee - qty*exit_p*fee
                satellite_cash += pnl
                trades.append({'dt':df['dt'].iloc[i],'r':(exit_p-entry)/risk,'pnl':pnl})
                in_pos=False
                exit_pending=None
        unrl = qty*(row['close']-entry) if in_pos else 0
        curve.append(core_btc*row['close']+satellite_cash+unrl)

    curve=np.array(curve)
    peak=np.maximum.accumulate(curve)
    dd=((curve-peak)/peak).min()*100
    bh_dd = ((df['close'].values - np.maximum.accumulate(df['close'].values))/np.maximum.accumulate(df['close'].values)).min()*100

    print(f"\n--- HYBRID: giu 1 BTC + margin them theo tin hieu ({label}) ---")
    print(f"Gia tri cuoi: ${curve[-1]:,.0f}  (x{curve[-1]/start_price:.2f})  so voi Buy&Hold thuan: ${end_price:,.0f} (x{end_price/start_price:.2f})")
    print(f"Dong gop rieng cua phan margin: ${satellite_cash:,.0f}  |  So lenh margin: {len(trades)}")
    print(f"Max Drawdown Hybrid: {dd:.1f}%   |   Max Drawdown Buy&Hold thuan: {bh_dd:.1f}%")

END_DATE = '2025-09-30 23:59:59'  # moc chung de so sanh cong bang giua D1/H4/H1

h1 = pd.read_csv('../data/h1_full.csv', parse_dates=['dt'])
h4 = pd.read_csv('../data/h4_full.csv', parse_dates=['dt'])
h1 = h1[h1['dt'] <= END_DATE].reset_index(drop=True)
h4 = h4[h4['dt'] <= END_DATE].reset_index(drop=True)
d1_raw = h1.set_index('dt')[['open','high','low','close']].resample('1D').agg(
    {'open':'first','high':'max','low':'min','close':'last'}).dropna().reset_index()

H1_GAP_HOURS = 6.0  # H1 co 7 cho thieu 1-4 nen lien tiep (max cach nhau 5h): coi la lien mach, khong cat doan/reset EMA
h1p = prep(h1, H1_GAP_HOURS)
h4p = prep(h4, 4.1)
d1p = prep(d1_raw, 24.1)
# nen H1 (index theo dt) dung de xu ly SL trong nen vao lenh cua H4/D1
h1_sub = h1.set_index('dt')[['open','high','low','close']].sort_index()

t_h1 = run_backtest_atr(h1p, "KHUNG H1")
t_h4 = run_backtest_atr(h4p, "KHUNG H4", sub=h1_sub, bar_hours=4)
t_d1 = run_backtest_atr(d1p, "KHUNG D1", sub=h1_sub, bar_hours=24)

run_hybrid(h1p, "H1")
run_hybrid(h4p, "H4", sub=h1_sub, bar_hours=4)
run_hybrid(d1p, "D1", sub=h1_sub, bar_hours=24)

t_h1.to_csv('../results/trades_h1.csv', index=False)
t_h4.to_csv('../results/trades_h4.csv', index=False)
t_d1.to_csv('../results/trades_d1.csv', index=False)
