"""Bien the entry "pha dinh N nen gan nhat" (mac dinh N=5) so voi Breakout goc (pha dinh nen tin hieu).

Luat bien the:
  * Nen tin hieu: EMA9 cat len EMA45 voi EMA9 > EMA45 > EMA200 (giong Breakout goc).
  * Muc cho mua = dinh cao nhat cua N nen gan nhat TAI nen tin hieu, tinh ca nen tin hieu
    (nen tin hieu + N-1 nen truoc no). Muc nay co dinh, khong doi theo nen moi.
  * Vao lenh: nen dau tien co high > muc cho; khop o max(muc cho, gia mo cua).
  * SL, thoat lenh (breakdown day nen cat xuong), huy lenh cho, SL trong nen vao lenh, lam nong EMA,
    phi: giong het Breakout goc (prep/stop_in_entry_bar/stats copy tu full_track.py + asset_test.py).
  * lookback=1 -> dung bang Breakout goc (dung de doi chieu voi results/full_track_summary.csv).

Bien the phu de kiem tra do nhay:
  * include_signal=False: N nen TRUOC nen tin hieu (khong tinh nen tin hieu).
  * rolling=True: muc cho cap nhat moi nen = dinh N nen gan nhat cua nen vua dong (truot theo gia).

Du lieu: BTC H1 = h1_combined_2021_now.csv, H4 = h4_full.csv, D1 = resample tu H1; vang PAXG H1/H4.
Ngoai mau = lenh vao tu 1/10/2025 (cung moc voi README). Ket qua: results/breakout5_summary.csv,
results/breakout5_trades_btc_h1.csv, results/breakout5_trades_paxg_h4.csv.
"""
import pandas as pd
import numpy as np

WARMUP_BARS = 200  # EMA200 khoi tao tu nen dau -> can ~200 nen truoc khi tin tin hieu

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
        g['aligned'] = (g['EMA9'] > g['EMA45']) & (g['EMA45'] > g['EMA200'])
        # lam nong EMA: WARMUP_BARS nen dau cua moi doan chi dung de tinh EMA/ATR, khong duoc vao lenh
        g['aligned'] &= (np.arange(len(g)) >= WARMUP_BARS)
        return g
    df = df.groupby('seg', group_keys=False).apply(ci).reset_index(drop=True)
    df['gap_hours'] = df['dt'].diff().dt.total_seconds()/3600
    df['seg'] = (df['gap_hours'] > gap_thresh_hours).cumsum()
    return df

def stop_in_entry_bar(row, pending, sl, sub=None, bar_hours=None):
    """Nen vao lenh co cham SL sau khi khop khong? Co nen con (H1 cho H4/D1) thi duyet theo thu tu thoi gian,
    khong co thi gia dinh bat loi (cham SL la thua)."""
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

def run_breakout_n(df, atr_mult=2.5, lookback=5, include_signal=True, rolling=False, sub=None, bar_hours=None):
    """Breakout dinh N nen gan nhat khi EMA9 cat len EMA45. Exit: SL uu tien, khong thi cho breakdown day nen cat xuong."""
    # dinh N nen ket thuc tai nen i (tinh ca nen i) hoac ket thuc tai nen i-1; chi lay nen cung doan du lieu
    hh_in = df.groupby('seg')['high'].transform(lambda s: s.rolling(lookback, min_periods=1).max())
    hh_ex = df.groupby('seg')['high'].transform(lambda s: s.shift(1).rolling(lookback, min_periods=1).max())
    hh = (hh_in if include_signal else hh_ex.fillna(df['high'])).values
    in_pos=False; entry=None; sl=None; pending=None; risk=None; entry_i=None; sig_i=None
    exit_pending=None
    trades=[]
    for i in range(1, len(df)):
        row = df.iloc[i]; prev = df.iloc[i-1]
        if not in_pos:
            if pending is not None and prev['cross_down']:
                pending = None  # EMA9 cat xuong EMA45 truoc khi breakout -> huy lenh cho mua
            if prev['cross_up'] and prev['aligned']:
                pending = hh[i-1]; sig_i = i-1  # dinh N nen gan nhat tai nen tin hieu
            elif rolling and pending is not None:
                pending = hh[i-1]  # bien the truot: cap nhat theo nen vua dong
            if pending is not None:
                if row['high'] > pending and prev['aligned']:
                    entry = max(pending, row['open']); sl = entry - atr_mult*prev['ATR14']
                    if entry > sl:
                        in_pos=True; entry_i=i; risk=entry-sl
                        base = {'signal_dt': df['dt'].iloc[sig_i], 'entry_dt': row['dt'], 'bars_to_fill': i-sig_i,
                                'signal_high': df['high'].iloc[sig_i], 'level': pending, 'entry': entry, 'sl': sl}
                        if stop_in_entry_bar(row, pending, sl, sub, bar_hours):  # cham SL ngay trong nen vao lenh
                            trades.append({**base, 'exit_dt': row['dt'], 'exit': sl, 'r': -1.0})
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
                trades.append({**base, 'exit_dt': row['dt'], 'exit': exit_p, 'r': (exit_p-entry)/risk})
                in_pos=False
                exit_pending=None
    return pd.DataFrame(trades)

def stats(t, fee=0.0):
    if t is None or len(t) == 0:
        return None
    r = t['r'] - fee*(t['entry']+t['exit'])/(t['entry']-t['sl'])
    w = r[r>0]; l = r[r<=0]
    pf = w.sum()/abs(l.sum()) if len(l) and l.sum()!=0 else float('inf')
    c = pd.concat([pd.Series([0.0]), r.cumsum()], ignore_index=True); dd = (c-c.cummax()).min()
    return {'lenh': len(r), 'winrate': len(w)/len(r)*100, 'pf': pf, 'expectancy': r.mean(),
            'tong_r': r.sum(), 'max_dd': dd, 'r_dd': r.sum()/abs(dd) if dd < 0 else float('inf')}

def load(h1_path, h4_path):
    h1 = pd.read_csv(h1_path, parse_dates=['dt'])
    h4 = pd.read_csv(h4_path, parse_dates=['dt'])
    d1_raw = h1.set_index('dt')[['open','high','low','close']].resample('1D').agg(
        {'open':'first','high':'max','low':'min','close':'last'}).dropna().reset_index()
    if h1['dt'].max().hour != 23:  # ngay cuoi chua du 24 nen H1 -> bo ngay do khoi D1
        d1_raw = d1_raw[d1_raw['dt'] < h1['dt'].max().normalize()].reset_index(drop=True)
    h1_sub = h1.set_index('dt')[['open','high','low','close']].sort_index()
    frames = {'D1': prep(d1_raw, 24.1), 'H4': prep(h4, 4.1), 'H1': prep(h1, H1_GAP_HOURS)}
    sub_args = {'D1': dict(sub=h1_sub, bar_hours=24), 'H4': dict(sub=h1_sub, bar_hours=4), 'H1': {}}
    return frames, sub_args

IS_END = pd.Timestamp('2025-10-01')
FEE = 0.0004  # 0.04%/chieu (taker futures Binance)
H1_GAP_HOURS = 6.0  # H1 co 7 cho thieu 1-4 nen lien tiep: coi la lien mach
ATR_MULTS = [1.5, 2.0, 2.5, 3.0, 3.5]
# (ten, tham so entry): Goc = pha dinh nen tin hieu; Dinh5 = luat moi; con lai = kiem tra do nhay
VARIANTS = [('Goc (dinh nen tin hieu)', dict(lookback=1)),
            ('Dinh 5 nen (gom nen TH)', dict(lookback=5)),
            ('Dinh 5 nen truoc nen TH', dict(lookback=5, include_signal=False)),
            ('Dinh 5 nen truot', dict(lookback=5, rolling=True)),
            ('Dinh 3 nen (gom nen TH)', dict(lookback=3)),
            ('Dinh 10 nen (gom nen TH)', dict(lookback=10))]
ASSETS = [('BTC', '../data/h1_combined_2021_now.csv', '../data/h4_full.csv'),
          ('PAXG', '../data/paxg_h1.csv', '../data/paxg_h4.csv')]
TRADE_LISTS = {('BTC', 'H1', 2.5), ('PAXG', 'H4', 2.0)}  # cau hinh tot nhat cua README -> luu chi tiet lenh

if __name__ == '__main__':
    rows = []
    for name, h1_path, h4_path in ASSETS:
        frames, sub_args = load(h1_path, h4_path)
        for tf, dfp in frames.items():
            if name == 'PAXG' and tf == 'D1':
                continue  # PAXG D1 chi ~12 lenh, khong du ket luan
            print(f"\n{'='*118}\n{name} {tf}: {dfp['dt'].iloc[0].date()} -> {dfp['dt'].iloc[-1].date()}  ({len(dfp)} nen)\n{'='*118}")
            print(f"{'':>31} | {'TOAN BO, DA TRU PHI 0.04%/chieu':^50} | {'IN-SAMPLE':^14} | {'NGOAI MAU (tu 10/2025)':^24}")
            print(f"{'Entry':>24} {'ATR':>5} | {'Lenh':>4} {'Win':>6} {'PF':>5} {'Expect':>8} {'Tong R':>8} {'MaxDD':>7} {'R/DD':>5} | {'Lenh':>4} {'PF':>5}   | {'Lenh':>4} {'PF':>5} {'Tong R':>8}")
            for m in ATR_MULTS:
                for label, kw in VARIANTS:
                    t = run_breakout_n(dfp, atr_mult=m, **kw, **sub_args[tf])
                    ti = t[t['entry_dt'] < IS_END]; to = t[t['entry_dt'] >= IS_END]
                    f = stats(t, FEE); a = stats(ti, FEE); b = stats(to, FEE)
                    rows.append({'tai_san': name, 'khung': tf, 'entry': label, 'atr': m,
                                 'nen_cho_tb': t['bars_to_fill'].mean(),
                                 **{'full_'+k: v for k, v in (f or {}).items()},
                                 **{'is_'+k: v for k, v in (a or {}).items()},
                                 **{'oos_'+k: v for k, v in (b or {}).items()}})
                    sa = f"{a['lenh']:>4} {a['pf']:>5.2f}" if a else f"{0:>4} {'-':>5}"
                    sb = f"{b['lenh']:>4} {b['pf']:>5.2f} {b['tong_r']:>+7.2f}R" if b else f"{0:>4} {'-':>5} {'-':>8}"
                    print(f"{label:>24} {m:>4.1f}x | {f['lenh']:>4} {f['winrate']:>5.1f}% {f['pf']:>5.2f} {f['expectancy']:>+7.3f}R "
                          f"{f['tong_r']:>+7.1f}R {f['max_dd']:>6.1f}R {f['r_dd']:>5.2f} | {sa}   | {sb}")
                    if (name, tf, m) in TRADE_LISTS and kw == dict(lookback=5):
                        t.round({c: 4 for c in ['signal_high', 'level', 'entry', 'sl', 'exit', 'r']}).to_csv(f"../results/breakout5_trades_{name.lower()}_{tf.lower()}.csv", index=False)
                print('-'*118)

    pd.DataFrame(rows).round(3).to_csv('../results/breakout5_summary.csv', index=False)
    print("\nDa luu: results/breakout5_summary.csv, results/breakout5_trades_btc_h1.csv, results/breakout5_trades_paxg_h4.csv")
