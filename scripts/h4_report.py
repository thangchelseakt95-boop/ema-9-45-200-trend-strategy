"""Bang thong ke day du khung H4 cho BTC/USDT: Breakout (ATR 1.0-4.0) va Pullback V5 (ATR 1.5-3.0).
Dung nguyen cac ham prep/stop_in_entry_bar/run_breakout/run_pullback cua asset_test.py (khong doi logic),
SL trong nen vao lenh xu ly bang nen H1. Phi 0.04%/chieu quy ra R. Them mo phong von $1,000, rui ro 1%/lenh (lai kep).

Cach dung:  python h4_report.py ../data/btc_h1_binance.csv ../data/btc_h4_binance.csv
"""
import sys
import pandas as pd
import numpy as np

# Lay cac ham backtest tu asset_test.py (phan truoc 'IS_END' chi gom import + dinh nghia ham)
src = open('asset_test.py', encoding='utf-8').read()
exec(src[:src.index('IS_END = ')])

IS_END = pd.Timestamp('2025-10-01')
FEE = 0.0004
RISK = 0.01
BO_MULTS = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
PB_MULTS = [1.5, 2.0, 2.5, 3.0]

def r_net(t, fee):
    return t['r'] - fee*(t['entry']+t['exit'])/(t['entry']-t['sl'])

def stats(r):
    if len(r) == 0:
        return None
    w = r[r > 0]; l = r[r <= 0]
    pf = w.sum()/abs(l.sum()) if len(l) and l.sum() != 0 else float('inf')
    c = pd.concat([pd.Series([0.0]), r.cumsum()], ignore_index=True); dd = (c-c.cummax()).min()
    # chuoi thua dai nhat
    streak = mx = 0
    for x in r:
        streak = streak+1 if x <= 0 else 0; mx = max(mx, streak)
    eq = 1000*np.cumprod(1+RISK*r.values)
    peak = np.maximum.accumulate(np.concatenate([[1000], eq]))
    eq_dd = ((np.concatenate([[1000], eq])-peak)/peak).min()*100
    return {'lenh': len(r), 'winrate': len(w)/len(r)*100, 'pf': pf, 'expectancy': r.mean(),
            'tong_r': r.sum(), 'max_dd': dd, 'r_dd': r.sum()/abs(dd) if dd < 0 else float('inf'),
            'avg_win': w.mean() if len(w) else 0.0, 'max_win': r.max(), 'chuoi_thua': mx,
            'von_cuoi': eq[-1], 'dd_von_pct': eq_dd}

h1 = pd.read_csv(sys.argv[1], parse_dates=['dt'])
h4 = pd.read_csv(sys.argv[2], parse_dates=['dt'])
h1_sub = h1.set_index('dt')[['open','high','low','close']].sort_index()
dfp = prep(h4, 4.1)
print(f"BTC/USDT H4: {dfp['dt'].iloc[0]} -> {dfp['dt'].iloc[-1]} ({len(dfp)} nen, {dfp['seg'].nunique()} doan); "
      f"in-sample = lenh vao truoc {IS_END.date()}, phi {FEE*100:.2f}%/chieu, von $1,000 rui ro {RISK*100:.0f}%/lenh")

rows = []
for strat, fn, mults in [('Breakout', run_breakout, BO_MULTS), ('Pullback V5', run_pullback, PB_MULTS)]:
    for m in mults:
        t = fn(dfp, atr_mult=m, sub=h1_sub, bar_hours=4)
        r = r_net(t, FEE).reset_index(drop=True)
        f = stats(r)
        ins = stats(r[t['entry_dt'].values < np.datetime64(IS_END)].reset_index(drop=True))
        oos = stats(r[t['entry_dt'].values >= np.datetime64(IS_END)].reset_index(drop=True))
        f01 = stats(r_net(t, 0.001).reset_index(drop=True))
        rows.append({'chien_luoc': strat, 'atr': m, **f,
                     'is_lenh': ins['lenh'] if ins else 0, 'is_pf': ins['pf'] if ins else np.nan,
                     'oos_lenh': oos['lenh'] if oos else 0, 'oos_thang': int((r[t['entry_dt'].values >= np.datetime64(IS_END)] > 0).sum()),
                     'oos_pf': oos['pf'] if oos else np.nan, 'oos_tong_r': oos['tong_r'] if oos else 0.0,
                     'pf_phi01': f01['pf']})

df = pd.DataFrame(rows)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print(df.round(3).to_string(index=False))
df.round(3).to_csv('../results/h4_report.csv', index=False)
c = h4['close'].values
print(f"Buy & Hold: {c[0]:,.2f} -> {c[-1]:,.2f} (x{c[-1]/c[0]:.2f}), Max DD {((c-np.maximum.accumulate(c))/np.maximum.accumulate(c)).min()*100:.1f}%")
print("Da luu: ../results/h4_report.csv")
