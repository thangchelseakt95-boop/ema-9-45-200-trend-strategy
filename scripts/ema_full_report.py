"""Bang thong ke day du cho mot cap EMA (vd 10/50): H1/H4/D1, Breakout va Pullback V5, ATR 1.0-4.0.
Cung luat voi asset_test.py (loc EMA nhanh > EMA cham > EMA200, lam nong 200 nen, SL = k x ATR(14), SL trong nen
vao lenh xu ly bang nen H1 cho H4/D1), chi thay chu ky EMA. Phi 0.04%/chieu quy ra R; them PF khi phi 0.1%/chieu,
tach trong mau / ngoai mau (lenh vao tu 1/10/2025), mo phong von $1,000 rui ro 1%/lenh (lai kep).
ATR toi uu = muc co Tong R / |Max DD| (R/DD) cao nhat sau phi.

Cach dung:  python ema_full_report.py ../data/btc_h1_binance.csv ../data/btc_h4_binance.csv BTC 10 50 [A|B]
            (B = bo loc "EMA nhanh > EMA cham va gia > EMA200"; mac dinh A = "EMA nhanh > EMA cham > EMA200")
"""
import sys
import pandas as pd
import numpy as np

h1_path, h4_path, name, FAST, SLOW = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
FILTER = sys.argv[6].upper() if len(sys.argv) > 6 else 'A'

src = open('asset_test.py', encoding='utf-8').read()
funcs = src[:src.index('IS_END = ')]
assert "span=9," in funcs and "span=45," in funcs
ns = {}
assert "g['aligned'] = (g['EMA9'] > g['EMA45']) & (g['EMA45'] > g['EMA200'])" in funcs
if FILTER == 'B':  # bo loc B: EMA nhanh > EMA cham va gia dong cua > EMA200 (thay vi EMA nhanh > EMA cham > EMA200)
    funcs = funcs.replace("(g['EMA45'] > g['EMA200'])", "(g['close'] > g['EMA200'])")
exec(funcs.replace("span=9,", f"span={FAST},").replace("span=45,", f"span={SLOW},"), ns)

IS_END = np.datetime64('2025-10-01')
FEE, FEE_HIGH, RISK = 0.0004, 0.001, 0.01
MULTS = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]

def r_net(t, fee):
    return (t['r'] - fee*(t['entry']+t['exit'])/(t['entry']-t['sl'])).reset_index(drop=True)

def stats(r):
    if len(r) == 0:
        return None
    w = r[r > 0]; l = r[r <= 0]
    pf = w.sum()/abs(l.sum()) if l.sum() != 0 else float('inf')
    c = np.concatenate([[0], r.cumsum()]); dd = (c-np.maximum.accumulate(c)).min()
    streak = mx = 0
    for x in r:
        streak = streak+1 if x <= 0 else 0; mx = max(mx, streak)
    eq = np.concatenate([[1000], 1000*np.cumprod(1+RISK*r.values)])
    return {'lenh': len(r), 'winrate': len(w)/len(r)*100, 'pf': pf, 'expectancy': r.mean(), 'tong_r': r.sum(),
            'max_dd': dd, 'r_dd': r.sum()/abs(dd) if dd < 0 else float('inf'),
            'avg_win': w.mean() if len(w) else 0.0, 'avg_loss': l.mean() if len(l) else 0.0, 'max_win': r.max(),
            'chuoi_thua': mx, 'von_cuoi': eq[-1], 'dd_von_pct': ((eq-np.maximum.accumulate(eq))/np.maximum.accumulate(eq)).min()*100}

h1 = pd.read_csv(h1_path, parse_dates=['dt'])
h4 = pd.read_csv(h4_path, parse_dates=['dt'])
d1_raw = h1.set_index('dt')[['open','high','low','close']].resample('1D').agg(
    {'open':'first','high':'max','low':'min','close':'last'}).dropna().reset_index()
if h1['dt'].max().hour != 23:
    d1_raw = d1_raw[d1_raw['dt'] < h1['dt'].max().normalize()].reset_index(drop=True)
h1_sub = h1.set_index('dt')[['open','high','low','close']].sort_index()
frames = {'H1': (ns['prep'](h1, 6.0), {}), 'H4': (ns['prep'](h4, 4.1), dict(sub=h1_sub, bar_hours=4)),
          'D1': (ns['prep'](d1_raw, 24.1), dict(sub=h1_sub, bar_hours=24))}

rows = []
for tf, (dfp, kw) in frames.items():
    print(f"{name} {tf}: {dfp['dt'].iloc[0]} -> {dfp['dt'].iloc[-1]} ({len(dfp)} nen, {dfp['seg'].nunique()} doan)", flush=True)
    for strat, fn in [('Breakout', ns['run_breakout']), ('Pullback V5', ns['run_pullback'])]:
        for m in MULTS:
            t = fn(dfp, atr_mult=m, **kw)
            if len(t) == 0:
                continue
            r = r_net(t, FEE)
            oos_mask = t['entry_dt'].values >= IS_END
            f = stats(r); i = stats(r[~oos_mask].reset_index(drop=True)); o = stats(r[oos_mask].reset_index(drop=True))
            g = stats(r_net(t, 0.0)); h = stats(r_net(t, FEE_HIGH))
            rows.append({'tai_san': name, 'ema': f'{FAST}/{SLOW}', 'bo_loc': FILTER, 'khung': tf, 'chien_luoc': strat, 'atr': m, **f,
                         'pf_khong_phi': g['pf'], 'pf_phi01': h['pf'], 'r_dd_phi01': h['r_dd'],
                         'is_lenh': i['lenh'] if i else 0, 'is_pf': i['pf'] if i else np.nan,
                         'oos_lenh': o['lenh'] if o else 0, 'oos_thang': int((r[oos_mask] > 0).sum()),
                         'oos_pf': o['pf'] if o else np.nan, 'oos_tong_r': o['tong_r'] if o else 0.0})

df = pd.DataFrame(rows)
df['toi_uu'] = False
for (tf, st_), g in df.groupby(['khung', 'chien_luoc']):
    df.loc[g['r_dd'].idxmax(), 'toi_uu'] = True
pd.set_option('display.width', 300); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500)
print(df.round(3).to_string(index=False))
out = f"../results/ema{FAST}_{SLOW}{'_locB' if FILTER == 'B' else ''}_{name.lower()}.csv"
df.round(3).to_csv(out, index=False)
c = h1['close'].values
print(f"Buy & Hold {name}: {c[0]:,.2f} -> {c[-1]:,.2f} (x{c[-1]/c[0]:.2f}), Max DD {((c-np.maximum.accumulate(c))/np.maximum.accumulate(c)).min()*100:.1f}%")
print("Da luu:", out)
