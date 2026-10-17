"""Thong ke EUR/USD va USD/EUR voi phi forex sat thuc te (0.005%/chieu) va khong phi.
Dung nguyen cac ham cua asset_test.py. Cach dung: python fx_fee_check.py"""
import pandas as pd, numpy as np
src = open('asset_test.py', encoding='utf-8').read()
exec(src[:src.index('IS_END = ')])
IS_END = np.datetime64('2025-10-01')
def st(t, fee):
    r = t['r'] - fee*(t['entry']+t['exit'])/(t['entry']-t['sl'])
    w = r[r > 0]; l = r[r <= 0]
    pf = w.sum()/abs(l.sum()) if l.sum() != 0 else float('inf')
    c = np.concatenate([[0], r.cumsum()]); dd = (c-np.maximum.accumulate(c)).min()
    return len(r), len(w)/len(r)*100, pf, r.mean(), r.sum(), dd
rows = []
for name, f1, f4 in [('EUR/USD','../data/eurusdt_h1.csv','../data/eurusdt_h4.csv'), ('USD/EUR','../data/usdeur_h1.csv','../data/usdeur_h4.csv')]:
    h1 = pd.read_csv(f1, parse_dates=['dt']); h4 = pd.read_csv(f4, parse_dates=['dt'])
    sub = h1.set_index('dt')[['open','high','low','close']].sort_index()
    fr = {'H4': (prep(h4, 4.1), dict(sub=sub, bar_hours=4)), 'H1': (prep(h1, 6.0), {})}
    for tf, (dfp, kw) in fr.items():
        atr_pct = (dfp['ATR14']/dfp['close']).median()*100
        for strat, fn, ms in [('Breakout', run_breakout, [1.5, 2.0, 2.5, 3.0, 4.0]), ('Pullback V5', run_pullback, [2.0, 2.5, 3.0])]:
            for m in ms:
                t = fn(dfp, atr_mult=m, **kw)
                fee_r = (0.0004*(t['entry']+t['exit'])/(t['entry']-t['sl'])).mean()
                a = st(t, 0.0); b = st(t, 0.00005)
                o = t[t['entry_dt'].values >= IS_END]; ob = st(o, 0.00005) if len(o) else None
                rows.append(dict(cap=name, khung=tf, chien_luoc=strat, atr=m, atr_pct=atr_pct, phi004_R_moi_lenh=fee_r,
                                 lenh=a[0], winrate=b[1], pf_khong_phi=a[2], pf_phi0005=b[2], ky_vong=b[3], tong_r=b[4], max_dd=b[5],
                                 oos_lenh=ob[0] if ob else 0, oos_pf=ob[2] if ob else np.nan, oos_tong_r=ob[4] if ob else 0))
df = pd.DataFrame(rows)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print(df.round(3).to_string(index=False))
df.round(3).to_csv('../results/eurusd_fx_fee.csv', index=False)
