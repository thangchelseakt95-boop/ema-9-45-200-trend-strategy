"""So sanh cach "bat dau cho Pullback" (Pullback V5, EMA9/45):
  * hien tai: chi bat dau cho khi nen EMA9 cat len EMA45 da thoa bo loc xu huong;
  * moi (arm_any): bat dau cho o MOI lan EMA9 cat len EMA45, ke ca khi luc do chua thoa bo loc (vd gia con duoi EMA200)
    -> neu bo lo Breakout, khi gia da thoa bo loc va hoi ve EMA45 thi van vao lenh Pullback.
Nen tin hieu Pullback va nen truoc nen vao lenh van phai thoa bo loc (nhu cu). Bo loc A = EMA9 > EMA45 > EMA200,
B = EMA9 > EMA45 va gia > EMA200. Dung nguyen cac ham cua asset_test.py. Phi 0.04%/chieu; ngoai mau = lenh vao tu 1/10/2025.

Cach dung:  python pullback_arm_test.py
"""
import pandas as pd
import numpy as np

src = open('asset_test.py', encoding='utf-8').read()
funcs = src[:src.index('IS_END = ')]
ARM_OLD = "            if prev['cross_up'] and prev['aligned']:\n                waiting = True"
assert funcs.count(ARM_OLD) == 1

def load(filt, arm_any):
    f = funcs
    if filt == 'B':
        f = f.replace("(g['EMA45'] > g['EMA200'])", "(g['close'] > g['EMA200'])")
    if arm_any:
        f = f.replace(ARM_OLD, "            if prev['cross_up']:\n                waiting = True")
    ns = {}
    exec(f, ns)
    return ns

IS_END = np.datetime64('2025-10-01')
FEE = 0.0004

def stats(t):
    if len(t) == 0:
        return dict(lenh=0)
    r = (t['r'] - FEE*(t['entry']+t['exit'])/(t['entry']-t['sl'])).reset_index(drop=True)
    w = r[r > 0]; l = r[r <= 0]
    c = np.concatenate([[0], r.cumsum()]); dd = (c-np.maximum.accumulate(c)).min()
    s = r.sort_values(ascending=False)
    o = r[t['entry_dt'].values >= IS_END]
    pf = lambda x: x[x > 0].sum()/abs(x[x <= 0].sum()) if (x <= 0).any() else float('inf')
    return dict(lenh=len(r), winrate=len(w)/len(r)*100, pf=pf(r), ky_vong=r.mean(), tong_r=r.sum(), max_dd=dd,
                r_dd=r.sum()/abs(dd) if dd < 0 else float('inf'), pf_bo5=pf(s.iloc[5:]),
                oos_lenh=len(o), oos_pf=pf(o) if len(o) else np.nan, oos_tong_r=o.sum())

cfg = [('BTC', 'H1', '../data/btc_h1_binance.csv', None), ('BTC', 'H4', '../data/btc_h4_binance.csv', '../data/btc_h1_binance.csv'),
       ('PAXG', 'H1', '../data/paxg_h1_binance.csv', None), ('PAXG', 'H4', '../data/paxg_h4_binance.csv', '../data/paxg_h1_binance.csv')]
rows = []
variants = {(fl, arm): load(fl, arm) for fl in 'AB' for arm in (False, True)}
for name, tf, path, subpath in cfg:
    raw = pd.read_csv(path, parse_dates=['dt'])
    kw = {}
    if subpath:
        h1 = pd.read_csv(subpath, parse_dates=['dt'])
        kw = dict(sub=h1.set_index('dt')[['open','high','low','close']].sort_index(), bar_hours=4)
    gap = 6.0 if tf == 'H1' else 4.1
    for (fl, arm), ns in variants.items():
        dfp = ns['prep'](raw, gap)
        for m in [2.0, 2.5, 3.0]:
            t = ns['run_pullback'](dfp, atr_mult=m, **kw)
            rows.append(dict(tai_san=name, khung=tf, bo_loc=fl, cho_moi_lan_cat=arm, atr=m, **stats(t)))
        print(f"xong {name} {tf} loc {fl} arm_any={arm}", flush=True)

df = pd.DataFrame(rows)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30); pd.set_option('display.max_rows', 200)
print(df.round(3).to_string(index=False))
df.round(3).to_csv('../results/pullback_arm_test.csv', index=False)
print("Da luu: ../results/pullback_arm_test.csv")
