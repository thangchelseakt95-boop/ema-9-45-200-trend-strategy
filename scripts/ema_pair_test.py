"""So sanh cap EMA nhanh/cham (vd 9/45 voi 10/50) voi cung luat: loc EMA nhanh > EMA cham > EMA200, Breakout va
Pullback V5, SL = k x ATR(14), SL trong nen vao lenh xu ly bang nen H1 (H4/D1). Dung nguyen cac ham cua
asset_test.py, chi thay chu ky EMA. Phi 0.04%/chieu; ngoai mau = lenh vao tu 1/10/2025.

Cach dung:  python ema_pair_test.py ../data/btc_h1_binance.csv ../data/btc_h4_binance.csv BTC 9,45 10,50
"""
import sys
import pandas as pd
import numpy as np

src = open('asset_test.py', encoding='utf-8').read()
funcs = src[:src.index('IS_END = ')]
assert "span=9," in funcs and "span=45," in funcs

IS_END = np.datetime64('2025-10-01')
FEE = 0.0004
BO_MULTS = [1.5, 2.0, 2.5, 3.0, 3.5]
PB_MULTS = [1.5, 2.0, 2.5, 3.0]

def stats(t):
    if len(t) == 0:
        return None
    r = t['r'] - FEE*(t['entry']+t['exit'])/(t['entry']-t['sl'])
    w = r[r > 0]; l = r[r <= 0]
    pf = w.sum()/abs(l.sum()) if l.sum() != 0 else float('inf')
    c = np.concatenate([[0], r.cumsum()]); dd = (c-np.maximum.accumulate(c)).min()
    return {'lenh': len(r), 'winrate': len(w)/len(r)*100, 'pf': pf, 'expectancy': r.mean(), 'tong_r': r.sum(),
            'max_dd': dd, 'r_dd': r.sum()/abs(dd) if dd < 0 else float('inf')}

h1_path, h4_path, name = sys.argv[1], sys.argv[2], sys.argv[3]
pairs = [tuple(int(x) for x in p.split(',')) for p in sys.argv[4:]]
h1 = pd.read_csv(h1_path, parse_dates=['dt'])
h4 = pd.read_csv(h4_path, parse_dates=['dt'])
d1_raw = h1.set_index('dt')[['open','high','low','close']].resample('1D').agg(
    {'open':'first','high':'max','low':'min','close':'last'}).dropna().reset_index()
if h1['dt'].max().hour != 23:
    d1_raw = d1_raw[d1_raw['dt'] < h1['dt'].max().normalize()].reset_index(drop=True)
h1_sub = h1.set_index('dt')[['open','high','low','close']].sort_index()

rows = []
for fast, slow in pairs:
    ns = {}
    exec(funcs.replace("span=9,", f"span={fast},").replace("span=45,", f"span={slow},"), ns)
    frames = {'H1': (ns['prep'](h1, 6.0), {}), 'H4': (ns['prep'](h4, 4.1), dict(sub=h1_sub, bar_hours=4)),
              'D1': (ns['prep'](d1_raw, 24.1), dict(sub=h1_sub, bar_hours=24))}
    for tf, (dfp, kw) in frames.items():
        for strat, fn, mults in [('Breakout', ns['run_breakout'], BO_MULTS), ('Pullback V5', ns['run_pullback'], PB_MULTS)]:
            for m in mults:
                t = fn(dfp, atr_mult=m, **kw)
                f = stats(t)
                o = stats(t[t['entry_dt'].values >= IS_END]) if len(t) else None
                i = stats(t[t['entry_dt'].values < IS_END]) if len(t) else None
                rows.append({'tai_san': name, 'ema': f'{fast}/{slow}', 'khung': tf, 'chien_luoc': strat, 'atr': m,
                             **(f or {}), 'is_pf': i['pf'] if i else np.nan,
                             'oos_lenh': o['lenh'] if o else 0, 'oos_pf': o['pf'] if o else np.nan,
                             'oos_tong_r': o['tong_r'] if o else 0.0})
    print(f"xong EMA {fast}/{slow}", flush=True)

df = pd.DataFrame(rows)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30); pd.set_option('display.max_rows', 500)
print(df.round(3).to_string(index=False))
out = f"../results/ema_pair_{name.lower()}.csv"
df.round(3).to_csv(out, index=False)
print("Da luu:", out)
