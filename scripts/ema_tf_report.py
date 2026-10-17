"""Bang thong ke day du cho mot khung bat ky (vd 15m) va mot cap EMA: Breakout va Pullback V5, ATR 1.0-4.0.
Cung luat voi asset_test.py, chi thay chu ky EMA. Khong co nen nho hon de xet SL trong nen vao lenh nen dung gia
dinh bat loi (nhu H1, luu y #9). Phi 0.04%/chieu quy ra R; them PF khong phi va phi 0.1%; tach trong mau / ngoai mau
(lenh vao tu 1/10/2025); mo phong von $1,000 rui ro 1%/lenh. ATR toi uu = R/DD cao nhat sau phi.

Cach dung:  python ema_tf_report.py ../data/btc_m15_binance.csv BTC 15m 6.0 10 50 [A|B]
            (tham so: file CSV, ten, nhan khung, nguong gap tinh bang gio de chia doan, EMA nhanh, EMA cham)
"""
import sys
import pandas as pd
import numpy as np

path, name, tf, gap_h, FAST, SLOW = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
FILTER = sys.argv[7].upper() if len(sys.argv) > 7 else 'A'

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

raw = pd.read_csv(path, parse_dates=['dt'])
dfp = ns['prep'](raw, gap_h)
print(f"{name} {tf} EMA {FAST}/{SLOW}: {dfp['dt'].iloc[0]} -> {dfp['dt'].iloc[-1]} ({len(dfp)} nen, {dfp['seg'].nunique()} doan); "
      f"ATR trung vi = {(dfp['ATR14']/dfp['close']).median()*100:.3f}% gia", flush=True)

rows = []
for strat, fn in [('Breakout', ns['run_breakout']), ('Pullback V5', ns['run_pullback'])]:
    for m in MULTS:
        t = fn(dfp, atr_mult=m)
        if len(t) == 0:
            continue
        r = r_net(t, FEE)
        oos_mask = t['entry_dt'].values >= IS_END
        f = stats(r); i = stats(r[~oos_mask].reset_index(drop=True)); o = stats(r[oos_mask].reset_index(drop=True))
        g = stats(r_net(t, 0.0)); h = stats(r_net(t, FEE_HIGH))
        fee_r = (FEE*(t['entry']+t['exit'])/(t['entry']-t['sl'])).mean()
        rows.append({'tai_san': name, 'khung': tf, 'ema': f'{FAST}/{SLOW}', 'bo_loc': FILTER, 'chien_luoc': strat, 'atr': m, **f,
                     'phi_R_moi_lenh': fee_r, 'pf_khong_phi': g['pf'], 'tong_r_khong_phi': g['tong_r'], 'pf_phi01': h['pf'],
                     'is_lenh': i['lenh'] if i else 0, 'is_pf': i['pf'] if i else np.nan,
                     'oos_lenh': o['lenh'] if o else 0, 'oos_thang': int((r[oos_mask] > 0).sum()),
                     'oos_pf': o['pf'] if o else np.nan, 'oos_tong_r': o['tong_r'] if o else 0.0})
        print(f"  xong {strat} {m}x", flush=True)

df = pd.DataFrame(rows)
df['toi_uu'] = False
for _, g in df.groupby('chien_luoc'):
    df.loc[g['r_dd'].idxmax(), 'toi_uu'] = True
pd.set_option('display.width', 300); pd.set_option('display.max_columns', 40)
print(df.round(3).to_string(index=False))
out = f"../results/ema{FAST}_{SLOW}{'_locB' if FILTER == 'B' else ''}_{name.lower()}_{tf.lower()}.csv"
df.round(3).to_csv(out, index=False)
print("Da luu:", out)
