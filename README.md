# EMA 9/45/200 Trend Strategy — Breakout / Pullback

A long-only trend-following strategy built on three EMAs (9 / 45 / 200), with:

- a **TradingView Pine Script v6 strategy** you can paste into the Pine Editor, and
- the **Python backtest** it was researched with (BTC/USDT and PAXG/USDT, Jan 2021 → Sep 2026), including out-of-sample checks and fee sensitivity.

> **Not financial advice.** This is research on historical data. Past performance does not guarantee future results.

## The strategy

| Step | Rule |
|---|---|
| Trend filter | EMA9 > EMA45 > EMA200 (same timeframe). The first 200 bars are skipped while the EMAs warm up. |
| Signal | EMA9 crosses above EMA45 while the trend filter is true. |
| Entry — **Breakout** | Buy-stop at the high of the crossover bar. |
| Entry — **Pullback** | After the cross, wait for price to come back to EMA45. Signal bar = the first bar that touches EMA45 but closes above it, **or** (if price closes below EMA45) the first bar that closes back above it. Buy-stop at the high of that bar. |
| Pending order | Cancelled if EMA9 crosses back below EMA45 before it fills. One trade per crossover. |
| Stop loss | Entry − k × ATR(14), active from the entry bar (k = 2.5 by default). |
| Exit | When EMA9 crosses below EMA45: sell-stop at the low of that bar; cancelled if EMA9 crosses back above EMA45 first. |
| Sizing | Fixed % of equity at risk per trade (1% by default). |

Stops and entries are stop orders placed at bar close for the next bar. If the bar opens beyond the level (gap), the fill is at the open. No look-ahead, no repainting.

## Results (after 0.04% fee per side)

Full period **2021-01-01 → 2026-09-23**. Out-of-sample = trades entered after 2025-09-30 (the rules were tuned on data before that date). R = multiples of the initial risk.

### BTC/USDT

| Timeframe | Entry | ATR k | Trades | Win rate | Profit factor | Expectancy | Max DD | Out-of-sample | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **1H** | **Breakout** | **2.5** | 205 | 28.3% | **1.84** | +0.53R | −15.3R | PF 1.18 (28 trades) | **Best** |
| 1H | Pullback | 2.5 | 159 | 26.4% | 1.84 | +0.50R | −13.1R | PF 1.15 (23 trades) | Alternative |
| 4H | Breakout | 2.0 | 60 | 21.7% | 1.46 | +0.31R | −10.8R | 0 / 7 winners | Not recommended |
| 1D | Breakout | 2.5 | 11 | 45.5% | 2.96 | +0.85R | −2.0R | 1 trade | Too few trades |

### Gold (PAXG/USDT)

| Timeframe | Entry | ATR k | Trades | Win rate | Profit factor | Expectancy | Max DD | Out-of-sample | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **4H** | **Breakout** | 2.0 | 56 | 37.5% | 2.51 | +0.74R | −6.5R | PF 6.2 (8 trades) | **Best** |
| **4H** | **Pullback** | 2.5 | 40 | 45.0% | **2.79** | +0.71R | **−3.9R** | PF 2.35 (6 trades) | **Best (lower DD)** |
| 1H | Breakout | 4.0 | 214 | 35.0% | 1.53 | +0.20R | −19.3R | – | Breaks at 0.1% fees |
| 1D | Breakout | 2.5 | 11 | 54.5% | 9.75 | +3.45R | −1.7R | 0 trades | Too few trades |

### $1,000 simulation (BTC 1H Breakout 2.5×, 1% risk per trade, fees included)

| System | Final value | Max DD |
|---|---|---|
| Strategy signals only | $2,274 (×2.27) | **−17.3%** |
| Buy & hold BTC | $2,897 (×2.90) | −77.2% |

The strategy made less than buy & hold over this bull-market period but with a far smaller drawdown.

### Caveats

- **Low win rate (≈25–45%)**: most profit comes from a few large trends; losing streaks of 10+ trades are normal. Keep risk per trade small.
- **Favourable test period**: both BTC and gold rose strongly from 2021 to 2026. Expect weaker results in sideways or falling markets.
- **Small out-of-sample samples** (BTC 1H ≈ 28 trades, gold 4H 6–8 trades) and some **overfitting risk** (several ATR levels, two filters and five pullback variants were tried on the same data).
- **Slippage is not modelled** in the Python backtest — a bigger issue for thin PAXG liquidity. PAXG also trades on weekends, unlike spot gold.
- On 1H there is no lower-timeframe data, so a stop hit on the entry bar is resolved with the worst-case assumption. On 4H/1D the backtest uses 1H bars inside the entry bar.

## TradingView

File: [`tradingview/ema_9_45_200_trend_strategy.pine`](tradingview/ema_9_45_200_trend_strategy.pine) (a version with Vietnamese labels is in `ema_9_45_200_trend_strategy_vi.pine`).

1. Open TradingView → **Pine Editor** → create a new strategy and replace the code with the file's contents.
2. **Save**, then **Add to chart** (e.g. BINANCE:BTCUSDT 1H or BINANCE:PAXGUSDT 4H).
3. Check the **Strategy Tester** tab. Adjust *Entry type*, *Stop loss = k x ATR(14)* and *Risk per trade* in the settings.

Defaults: initial capital 1,000 USD, commission 0.04% per side, slippage 2 ticks, long only, no pyramiding.

On the chart: green = pending buy-stop, light red = **projected stop loss** (buy-stop − k × ATR, shown as soon as an order is pending), red = active stop loss, fuchsia = pending exit level. On the last bar the active levels are also drawn as dashed lines extending right with price labels. ATR(14) and the stop distance are shown in the Data Window. The script's ATR is an EMA of the true range (same as the Python backtest), so it differs slightly from TradingView's built-in ATR indicator (RMA / Wilder).

**Alerts:** at bar close the script fires `alert()` messages for: new pending buy-stop (with projected SL and SL distance), buy-stop cancelled, long filled (with stop loss), filled and stopped out on the same bar, new exit stop (with the active stop), exit stop cancelled, and position closed. To enable: on the chart click **Alert** → Condition: this strategy → **"alert() function calls only"** → choose notifications → Create. One alert covers all events. Re-create the alert after editing the script (alerts run on the script version they were created with). The script does not place orders on your exchange.

TradingView results will differ from the Python backtest: TradingView loads a limited number of historical bars (depending on your plan), its broker emulator decides same-bar stop fills from OHLC (or Bar Magnifier), and if the stop loss and the exit level are both hit in one bar the script fills the higher level. On BTCUSDT 1H (Jan–Sep 2026) the script gave 20 trades / PF 1.26 versus 24 trades / PF 1.33 in Python.

## Python backtest

```bash
pip install -r requirements.txt
cd scripts
python full_track.py          # full track record 2021 → 2026 for 1H / 4H / 1D, ATR 1.0–4.0 → results/full_track_summary.csv
python oos_test.py            # out-of-sample check (Breakout)
python oos_pullback_test.py   # out-of-sample check (Breakout and Pullback)
python pullback_test.py       # Breakout vs Pullback, in-sample
python backtest_main.py       # in-sample 2021 → Sep 2025 statistics + trade lists
python asset_test.py ../data/paxg_h1.csv ../data/paxg_h4.csv PAXG   # any asset
python download_binance.py PAXGUSDT 4h ../data/paxg_h4.csv          # fetch closed candles from the Binance public API
```

| Folder | Contents |
|---|---|
| `data/` | Binance BTC/USDT candles (1H, 4H, 1D) and PAXG/USDT candles (1H, 4H) from 2021; end dates per file are listed in the research notes |
| `scripts/` | Backtest engine and experiments (comments and console output are in Vietnamese) |
| `results/` | Summary tables and per-trade lists |
| `tradingview/` | Pine Script strategy |
| `docs/research-notes-vi.md` | Full research log in Vietnamese: every table, the bugs found and fixed (off-by-one bar, unrealistic fills, stop hit on the entry bar, EMA warm-up, data gaps), and independent verification |

Implementation notes: EMAs use pandas `ewm(adjust=False)` (the Pine script seeds its EMAs the same way); ATR is an EMA of the true range; the data is split into segments at gaps (> 6 h on 1H) and each segment gets its own 200-bar warm-up. Fees are converted to R as `fee × (entry + exit) / stop distance`.

## License

[Mozilla Public License 2.0](LICENSE). You may use, modify and share this code; modified versions of these files must stay open-source under the same license.
