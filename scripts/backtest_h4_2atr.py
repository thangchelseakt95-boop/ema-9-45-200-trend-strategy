import pandas as pd
import numpy as np

def run_backtest_atr(df, gap_thresh_hours, label, atr_mult=2.0):
    df = df.sort_values('dt').reset_index(drop=True)
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
        return g

    df = df.groupby('seg', group_keys=False).apply(ci).reset_index(drop=True)
    df['gap_hours'] = df['dt'].diff().dt.total_seconds()/3600
    df['seg'] = (df['gap_hours'] > gap_thresh_hours).cumsum()

    in_pos=False; entry=None; sl=None; pending=None
    trades=[]
    for i in range(1, len(df)):
        row = df.iloc[i]; prev = df.iloc[i-1]
        if not in_pos:
            if pending is not None:
                if row['high'] > pending and prev['above200']:
                    entry = pending
                    sl = entry - atr_mult*prev['ATR14']
                    if entry > sl:
                        in_pos = True
                        entry_i = i
                    pending = None
            if prev['cross_up'] and prev['above200']:
                pending = prev['high']
        else:
            exit_p=None
            if row['low'] <= sl:
                exit_p = sl
            elif row['cross_down']:
                exit_p = row['close']
            if exit_p is not None:
                risk = entry - sl
                r = (exit_p - entry)/risk
                trades.append({'entry_dt':df['dt'].iloc[entry_i],'exit_dt':row['dt'],'entry':entry,'sl':sl,'exit':exit_p,'r':r})
                in_pos=False

    tdf = pd.DataFrame(trades)
    wins = tdf[tdf['r']>0]
    losses = tdf[tdf['r']<=0]
    pf = wins['r'].sum() / abs(losses['r'].sum()) if len(losses) and losses['r'].sum()!=0 else float('inf')
    expectancy = tdf['r'].mean()
    cum = tdf['r'].cumsum()
    peak = cum.cummax()
    maxdd = (cum-peak).min()

    print(f"=== {label} ===")
    print(f"So lenh: {len(tdf)} | Win rate: {len(wins)/len(tdf)*100:.1f}% | Profit Factor: {pf:.2f}")
    print(f"Expectancy: {expectancy:+.3f}R | Tong R: {tdf['r'].sum():+.2f}R | Max DD: {maxdd:.2f}R")
    print(f"TB thang: {wins['r'].mean():.2f}R ({len(wins)}) | TB thua: {losses['r'].mean():.2f}R ({len(losses)})")

h4 = pd.read_csv('../data/h4_full.csv', parse_dates=['dt'])
run_backtest_atr(h4, 4.1, "H4 BTC SL=2xATR (2021-2026, sua loi cross)", atr_mult=2.0)
