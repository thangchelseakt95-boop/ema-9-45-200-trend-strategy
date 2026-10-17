# Backtest EMA9/EMA45 Crossover — BTC/USDT

> **Kết luận nhanh (BTC):** chỉ **H1 + Breakout + SL 2.5×ATR** còn lợi thế đáng tin (PF 1.84 sau phí, vẫn lãi ngoài mẫu). H4, D1 không nên dùng; Pullback V5 H1 2.5× có cùng PF nhưng lãi ít hơn và kém bền ngoài mẫu. Xem mục "Kết luận tổng hợp" ở cuối.
>
> **Vàng (PAXG/USDT):** khung tốt nhất là **H4 + Breakout + SL 2.0–3.5×ATR** (PF 2.4–2.6 sau phí, lãi phân bố đều hơn BTC), hoặc **Pullback V5 2.0–2.5×** (PF 2.5–2.8, DD nhẹ hơn) — nhưng được test trong giai đoạn vàng tăng rất mạnh. Xem mục "Vàng (PAXG/USDT)".

## Chiến lược gốc
- **Tín hiệu**: EMA9 cắt lên EMA45 = mua; EMA9 cắt xuống EMA45 = thoát lệnh.
- **Bộ lọc xu hướng**: 3 đường EMA phải xếp thứ tự "hoàn hảo" — EMA9 > EMA45 > EMA200 (cùng khung thời gian). Trước đây chỉ yêu cầu giá đóng cửa > EMA200, đã thay bằng điều kiện chặt hơn này (xem lưu ý #7).
- **Entry**: chờ giá breakout (vượt) đỉnh của cây nến tín hiệu (cây nến xảy ra cắt lên) rồi mới vào — không vào ngay tại điểm cắt.
- **Stop Loss**: entry − 2×ATR(14).
- **Thoát lệnh**: SL được ưu tiên kiểm tra trước; nếu chưa chạm SL và EMA9 cắt xuống EMA45, chờ giá breakdown (phá vỡ xuống) đáy của cây nến tín hiệu cắt xuống rồi mới thoát — đối xứng với luật entry, không thoát ngay tại giá đóng cửa như trước.
- **Hủy lệnh chờ**: lệnh chờ mua tự hủy nếu EMA9 cắt xuống EMA45 trước khi khớp; lệnh chờ thoát tự hủy nếu EMA9 cắt lên lại trước khi khớp (xem lưu ý #5).
- **Thời điểm khớp**: lệnh chờ có hiệu lực ngay từ cây nến liền sau nến tín hiệu; nếu giá mở cửa đã vượt mức chờ (gap) thì khớp ở giá mở cửa, không phải ở mức chờ (xem lưu ý #8).
- **SL trong nến vào lệnh**: nếu cây nến khớp lệnh cũng chạm SL thì tính là thua -1R ngay trong nến đó. Với H4/D1, dùng nến H1 bên trong để biết giá phá mức chờ trước hay chạm SL trước; với H1 (không có nến nhỏ hơn) dùng giả định bất lợi (xem lưu ý #9).
- **Làm nóng EMA**: 200 nến đầu của mỗi đoạn dữ liệu chỉ dùng để tính EMA/ATR, không được vào lệnh (`WARMUP_BARS = 200`, xem lưu ý #12).

### Biến thể Pullback V5 (`run_pullback` trong `pullback_test.py`, `oos_pullback_test.py`, `asset_test.py`; mặc định từ 28/9/2026)
Khác Breakout duy nhất ở cách chọn nến tín hiệu và điểm vào; SL, thoát lệnh, hủy lệnh chờ, khớp theo giá mở cửa, SL trong nến vào lệnh và làm nóng EMA giống hệt Breakout.
1. **Điều kiện mở đầu**: phải có EMA9 cắt lên EMA45 với EMA9 > EMA45 > EMA200 trước — sau đó mới bắt đầu "chờ pullback".
2. **Nến tín hiệu Pullback** — nhận cả hai kiểu hồi về EMA45 (trong lúc EMA9 vẫn trên EMA45 và 3 EMA vẫn xếp đúng thứ tự):
   - **Chạm rồi bật**: nến đầu tiên có giá thấp nhất chạm/xuyên EMA45 (low ≤ EMA45) nhưng **đóng cửa vẫn trên EMA45**.
   - **Cắt xuống rồi cắt lại**: nếu có nến **đóng cửa dưới EMA45** thì bỏ mức chờ (nếu có) và đợi nến **đầu tiên đóng cửa trở lại trên EMA45** — nến đó là nến tín hiệu. Nếu sau đó giá lại đóng cửa dưới EMA45 trước khi phá đỉnh, đợi lần cắt lại tiếp theo.
   Đặt lệnh chờ mua ở **đỉnh** của nến tín hiệu.
3. **Vào lệnh** khi giá phá đỉnh nến tín hiệu (bước xác nhận "bật lên"); khớp ở `max(đỉnh, giá mở cửa)`; nến ngay trước nến vào lệnh phải còn EMA9 > EMA45 > EMA200.
4. **Hủy chờ** nếu EMA9 cắt xuống EMA45 trước khi vào được lệnh.
5. Chi tiết cần biết: **mỗi lần cắt lên chỉ vào tối đa 1 lệnh** (kể cả bị SL ngay cũng không vào lại); SL tính theo ATR từ giá vào, không đặt dưới đáy nến pullback. Luật cũ (V1: nến đầu tiên có low ≤ EMA45, mức chờ cố định kể cả khi giá đóng cửa sâu dưới EMA45) vẫn chạy được bằng `run_pullback(..., variant='v1')` — xem lưu ý #14.

| | Breakout | Pullback V5 |
|---|---|---|
| Nến tín hiệu | Nến EMA9 cắt lên EMA45 | Nến chạm EMA45 rồi đóng cửa trên, hoặc nến đầu tiên đóng cửa trở lại trên EMA45 sau khi đã đóng cửa dưới |
| Vào lệnh | Phá đỉnh nến cắt lên | Phá đỉnh nến tín hiệu Pullback |
| SL và thoát lệnh | Giống nhau | Giống nhau |

## Cấu trúc thư mục
```
data/
  h1_full.csv          -> BTC/USDT khung H1, 2021-01-01 -> 2025-09-30 (có 7 chỗ thiếu 1–4 nến liền nhau, xem lưu ý #10) — dùng cho backtest chính (in-sample)
  h1_combined_2021_now.csv -> BTC/USDT H1, 2021-01-01 -> 2026-09-23 15:00 (= h1_full + h1_oos_binance, cùng 7 chỗ thiếu, đã bỏ nến chưa đóng) — dùng cho full_track.py
  d1_full.csv          -> BTC/USDT khung D1, resample từ H1, cùng giai đoạn
  h4_full.csv          -> BTC/USDT khung H4, 2021-01-01 -> 2026-09-23 12:00 (liền mạch, không gap, nến cuối đã đóng — đã vá bằng h4_oos_binance.csv ngày 26/9/2026, xem lưu ý #4)
  h1_oos_binance.csv   -> BTC/USDT H1, 2025-01-01 -> nay, tải trực tiếp từ Binance API, liền mạch — dùng cho validation out-of-sample
  h4_oos_binance.csv   -> BTC/USDT H4, 2025-01-01 -> nay, tải trực tiếp từ Binance API, liền mạch — dùng cho validation out-of-sample
  btc_h1_binance.csv, btc_h4_binance.csv -> BTC/USDT H1/H4 tải mới từ Binance, 2021-01-01 -> 2026-10-09 (dùng cho h4_report.py, ema_pair_test.py, ema_full_report.py)
  btc_m15_binance.csv -> BTC/USDT 15m, Binance, 2021-01-01 -> 2026-10-13 (dùng cho ema_tf_report.py)
  paxg_h1_binance.csv, paxg_h4_binance.csv -> Vàng PAXG/USDT H1/H4 tải mới, 2021-01-01 -> 2026-10-09 (dùng cho ema_full_report.py)
  eurusdt_h1.csv, eurusdt_h4.csv -> EUR/USDT (Binance) H1/H4, 2021-01-01 -> 2026-10-03; usdeur_h1.csv, usdeur_h4.csv = giá nghịch đảo (USD/EUR)
  paxg_h1.csv, paxg_h4.csv -> Vàng PAXG/USDT H1/H4, 2021-01-01 -> 2026-09-27, tải bằng download_binance.py (chỉ nến đã đóng)
scripts/
  backtest_main.py      -> Chạy backtest chính (breakout entry, breakdown exit, SL=2xATR) cho cả D1/H4/H1 + mô hình Hybrid, kết thúc 30/9/2025
  backtest_h4_2atr.py   -> Backtest H4 riêng, SL=2xATR
  pullback_test.py      -> So sánh Breakout entry vs Pullback entry (Pullback V5 mặc định, variant='v1' cho luật cũ)
  oos_test.py           -> Validation out-of-sample: warm-up từ 2025-01-01, chỉ tính lệnh vào SAU 30/9/2025
  full_track.py         -> Full track record D1/H4/H1 trên toàn bộ dữ liệu 2021 -> nay, ATR 1.0-4.0, lưu results/full_track_summary.csv
  oos_pullback_test.py  -> Validation out-of-sample cho Breakout VA Pullback (oos_test.py chỉ có Breakout)
  download_binance.py   -> Tải nến Binance (public API) cho cặp bất kỳ, lưu CSV dt,open,high,low,close,volume
  fx_fee_check.py       -> EUR/USD và USD/EUR với phí forex 0.005%/chiều và không phí, lưu results/eurusd_fx_fee.csv
  ema_tf_report.py      -> Bảng thống kê đầy đủ cho 1 khung bất kỳ (vd 15m) và 1 cặp EMA, lưu results/ema<nhanh>_<chậm>_<tên>_<khung>.csv
  ema_full_report.py    -> Bảng thống kê đầy đủ cho 1 cặp EMA (vd 10/50): H1/H4/D1, Breakout + Pullback V5, ATR 1.0-4.0, ATR tối ưu, ngoài mẫu, vốn $1,000; lưu results/ema<nhanh>_<chậm>_<tên>.csv
  ema_pair_test.py      -> So sánh các cặp EMA nhanh/chậm (9/45, 10/50, ...) cùng luật, H1/H4/D1, lưu results/ema_pair_<tên>.csv
  h4_report.py          -> Bảng thống kê đầy đủ H4 (Breakout + Pullback V5, sau phí, ngoài mẫu, vốn $1,000), lưu results/h4_report.csv
  asset_test.py         -> Backtest Breakout + Pullback (D1/H4/H1, in-sample/ngoài mẫu, phí 0.04%/0.1%) cho tài sản bất kỳ, lưu results/<ten>_summary.csv
results/
  trades_d1.csv, trades_h4.csv, trades_h1.csv  -> Chi tiết từng lệnh (ngày vào/ra, entry/SL/exit, R)
  full_track_summary.csv  -> Bảng tổng hợp full track record (khung × ATR: số lệnh, win rate, PF, expectancy, tổng R, Max DD, R/DD; cả bản chưa và đã trừ phí, cột hậu tố _phi)
  paxg_summary.csv      -> Kết quả vàng từ asset_test.py (khung × chiến lược × ATR; cột is_/oos_/full_phi004_/full_phi01_)
tradingview/
  ema_9_45_200_trend_strategy.pine    -> Strategy Pine Script v6, bản tiếng Anh (bản chính, MPL 2.0)
  ema_9_45_200_trend_strategy_vi.pine -> Cùng logic, nhãn tiếng Việt (xem mục "Chiến lược trên TradingView")
```

## Cách chạy lại
```bash
cd scripts
pip install pandas numpy
python3 backtest_main.py       # thống kê D1/H4/H1 + so sánh Hybrid vs Buy&Hold (in-sample, 2021-2025)
python3 pullback_test.py       # so sánh kiểu vào lệnh breakout vs pullback
python3 oos_test.py            # validation out-of-sample trên dữ liệu sau 30/9/2025
python3 full_track.py          # full track record 2021 -> nay cho cả 3 khung
python3 oos_pullback_test.py    # validation out-of-sample cho ca Breakout va Pullback
python3 asset_test.py ../data/paxg_h1.csv ../data/paxg_h4.csv PAXG   # vàng (tải dữ liệu trước bằng download_binance.py)
```

## Lưu ý kỹ thuật quan trọng (đã từng gây lỗi, đừng lặp lại)

1. **Lỗi cross_up/cross_down**: KHÔNG dùng `series.shift(1).fillna(False)` để tính tín hiệu cắt — trên một số phiên bản pandas, thao tác này trả về kiểu `object` thay vì `bool`, khiến phép `~` (NOT) sai, làm tín hiệu "cắt lên" bị giữ `True` liên tục nhiều nến thay vì đúng 1 nến. Luôn dùng:
   ```python
   shifted = series.shift(1, fill_value=False)   # ĐÚNG
   ```

2. **Binance timestamp**: file kline từ 2025 trở đi dùng đơn vị microseconds thay vì milliseconds. Luôn kiểm tra:
   ```python
   if df['open_time'].iloc[0] > 1e14:
       df['open_time'] = df['open_time'] // 1000
   ```

3. **Khoảng trống dữ liệu (data gaps)**: nếu ghép nhiều file theo tháng mà thiếu file nào, EMA/ATR sẽ bị tính sai ngay sau chỗ nối (nhảy giá đột ngột). Luôn tách đoạn (segment) tại các khoảng trống > 1 chu kỳ nến trước khi tính EMA/ATR/tín hiệu, KHÔNG tính xuyên qua gap:
   ```python
   df['gap_hours'] = df['dt'].diff().dt.total_seconds()/3600
   df['seg'] = (df['gap_hours'] > threshold).cumsum()
   df = df.groupby('seg', group_keys=False).apply(compute_indicators)
   ```

4. **So sánh công bằng giữa các khung thời gian**: file `h4_full.csv` được cập nhật dần và hiện có dữ liệu vượt xa mốc 30/9/2025 (đến 19/9/2026), kèm nhiều khoảng gap lớn trong năm 2026 do thiếu file tải về (không phải gap thị trường thật — đã xác minh bằng dữ liệu Binance API liên tục, không gap). Nếu backtest H4 trên toàn bộ file mà không cắt mốc, kết quả sẽ lệch khỏi D1/H1 (từng bị: 79 lệnh/PF 1.89 thay vì đúng 71 lệnh/PF 1.94). `backtest_main.py` đã thêm hằng số `END_DATE = '2025-09-30 23:59:59'` và lọc cả `h1`/`h4` theo mốc này trước khi tính toán — luôn giữ nguyên cutoff này (hoặc cập nhật đồng bộ cho cả 3 khung) khi dữ liệu được refresh thêm. **Cập nhật 26/9/2026**: đã vá toàn bộ gap bằng cách gộp `h4_oos_binance.csv` vào `h4_full.csv` (3,506 nến trùng khớp tuyệt đối, chênh lệch giá = 0); file giờ liền mạch 2021-01-01 → 2026-09-23. Cutoff `END_DATE` vẫn cần giữ để so sánh in-sample công bằng.

5. **Lệnh chờ (pending) tự hủy khi EMA đảo chiều** (áp dụng trong `backtest_main.py`, `oos_test.py`, `pullback_test.py`): lệnh chờ mua (breakout) bị hủy nếu EMA9 cắt xuống EMA45 trước khi giá phá đỉnh nến tín hiệu; lệnh chờ thoát (breakdown) bị hủy nếu EMA9 cắt lên lại EMA45 trước khi giá phá đáy nến cắt xuống. Trước đây lệnh chờ treo mãi cho đến khi khớp hoặc bị tín hiệu cùng chiều ghi đè — một số lệnh thắng lớn ở H4 (vd. 5/10/2021 +5.8R) đến từ các lệnh chờ "cũ" như vậy, nên H4 xấu đi khi đổi luật (PF 2.44→2.03), còn H1 tốt lên (PF 1.97→2.19). `backtest_h4_2atr.py` là script cũ (bộ lọc giá > EMA200) và chưa áp dụng luật này.

6. **Luật thoát lệnh (breakdown exit) thay thế luật đóng-cửa-ngay**: so sánh cho thấy chờ giá phá đáy nến cắt xuống rồi mới thoát cho kết quả tốt hơn rõ rệt ở H4 (PF 1.94→2.00, expectancy +0.503R→+0.581R) và cải thiện nhẹ ở H1, nhưng kém hơn ở D1 (mẫu quá nhỏ để tin cậy). Đã áp dụng luật này làm mặc định trong `backtest_main.py` (cả `run_backtest_atr` và `run_hybrid`).

7. **Bộ lọc xu hướng "3 EMA hoàn hảo" (aligned) thay thế "giá > EMA200"**: yêu cầu thêm `EMA45 > EMA200` (ngoài `EMA9 > EMA45` đã có sẵn từ chính tín hiệu cắt lên) lọc bỏ các tín hiệu xảy ra khi xu hướng dài hạn (EMA45 so với EMA200) chưa thực sự đảo chiều dù giá đã tạm vượt EMA200. Cải thiện toàn diện ở **H4** (62→50 lệnh, PF 2.00→2.44, expectancy +0.581R→+0.835R, Max DD giảm gần một nửa -9.31R→-5.00R). Ở **H1** cải thiện PF/expectancy nhưng có thể làm DD xấu đi tùy mức ATR. Ở **D1** tại ATR=2.0 mặc định thì không đổi lệnh nào, nhưng ở ATR cao hơn (3.0×) từng test riêng cho kết quả kém hơn — cẩn trọng khi kết hợp với ATR rộng ở D1. Đã áp dụng làm mặc định trong `backtest_main.py`.

8. **Lỗi lệch 1 nến khi xét breakout/breakdown (đã sửa 25/9/2026)**: trước đây vòng lặp kiểm tra khớp lệnh chờ TRƯỚC rồi mới đặt lệnh chờ mới từ nến tín hiệu, nên cây nến liền sau nến tín hiệu không bao giờ được xét breakout (entry) hay breakdown (exit) — lệnh chỉ được xét từ cây thứ hai. Nếu cây bị bỏ qua đã vượt mức chờ, backtest vẫn ghi giá khớp đúng bằng mức chờ dù giá thật đã chạy xa hơn. Đã sửa ở `backtest_main.py`, `oos_test.py`, `pullback_test.py`: đặt lệnh chờ trước rồi mới kiểm tra khớp; khớp ở `max(mức chờ, giá mở cửa)` cho entry và `min(mức, giá mở cửa)` cho SL/exit. Riêng `run_pullback` còn đổi điều kiện lọc lúc khớp từ nến hiện tại sang nến trước (tránh dùng giá đóng cửa chưa biết). Tác động của từng phần phụ thuộc thứ tự áp dụng (phân rã ở lưu ý #11; riêng việc khớp theo giá mở cửa, khi đứng một mình sau khi đã sửa lệch nến thì rất nhỏ, nhưng với logic cũ bỏ qua 1 nến rồi khớp ở mức chờ cũ thì lớn), và **làm kết quả xấu đi ở cả 3 khung** — tức kết quả cũ đã được "tô đẹp" bởi lỗi này: H4 2×ATR PF 2.03→1.61, expectancy +0.651R→+0.398R; H1 2×ATR PF 2.19→2.02; D1 2×ATR PF 2.03→1.57.

9. **SL trong nến vào lệnh (đã sửa 26/9/2026)**: trước đây SL chỉ được kiểm tra từ cây nến SAU nến vào lệnh, nên nếu chính cây nến khớp lệnh vừa vượt mức chờ vừa rơi xuống dưới SL, backtest bỏ qua lần chạm SL này. Nay xử lý bằng hàm `stop_in_entry_bar`:
   - **H4/D1**: duyệt các nến H1 bên trong nến vào lệnh theo thứ tự thời gian — tìm nến H1 đầu tiên phá mức chờ, rồi xem từ nến đó trở đi có nến H1 nào chạm SL không. Nếu giá chạm vùng SL *trước* khi breakout thì lệnh không bị dừng. Nếu không có dữ liệu H1 cho nến đó thì dùng giả định bất lợi.
   - **H1**: không có nến nhỏ hơn nên dùng **giả định bất lợi** (vào lệnh rồi mới chạm SL → thua -1R).
   - Kết quả dùng nến H1 (full track 2021 → 9/2026): H4 1.0× chỉ còn 7/11 lệnh bị dừng thật trong nến vào, H4 1.5× còn 2/4, D1 1.0× còn 1/2 — một nửa số trường hợp theo giả định bất lợi là "báo động giả". Các lệnh bị dừng thật đó dù sao cũng thua -1R ở nến sau, nên số liệu H4 1.5× và D1 1.0× quay về gần như trước khi sửa, còn H4 1.0× vẫn lỗ nặng (PF 0.44 sau khi làm nóng EMA). Từ 2.0×ATR trở lên ở H4/D1 không có trường hợp nào.
   - H1: 37/223 lệnh ở 1.0×, 16 ở 1.5×, 8 ở 2.0×, 2 ở 2.5–3.0× bị dừng trong nến vào (giả định bất lợi). Một số cấu hình H1 còn tốt lên nhẹ vì lệnh bị dừng sớm giúp bắt được tín hiệu kế tiếp và tránh các lần thoát tệ hơn -1R do gap ở nến sau.
   - Đã áp dụng ở `backtest_main.py` (cả Hybrid), `oos_test.py`, `pullback_test.py`, `full_track.py`.

10. **Kiểm tra chất lượng dữ liệu (26/9/2026)**:
   - **Dữ liệu sạch**: không trùng timestamp, không NaN, không nến OHLC vô lý. H4 khớp 100% với H1 gộp lại (12,541 nến so sánh được), `h1_combined_2021_now.csv` khớp 100% `h1_full.csv` ở phần chung.
   - **H1 có 7 chỗ thiếu nến (tổng 14 giờ)**: 11/2/2021, 6/3/2021, 20/4/2021, 25/4/2021, 13/8/2021, 29/9/2021, 24/3/2023 (thiếu 1–4 nến liền nhau; nhiều khả năng sàn bảo trì, chưa xác minh). H4 không có các chỗ thiếu này. Trước đây code cắt đoạn ở mỗi chỗ thiếu và tính lại EMA từ đầu, nên ~8 ngày sau mỗi chỗ thiếu EMA200 chưa hội tụ và tín hiệu kém tin cậy. Nay `H1_GAP_HOURS = 6.0`: coi H1 là liền mạch (EMA/ATR tính xuyên qua chỗ thiếu ngắn; chỉ 14 nến trên ~50k). Tác động: **H1 kém đi nhẹ** (full track 2.5× PF 2.12→2.02, Hybrid H1 x5.27→x4.88, DD -75%→-79.4%); H4/D1 không đổi. Gap lớn hơn 6h vẫn được cắt đoạn.
   - **Đã bỏ nến chưa đóng ở cuối**: nến H1 16:00 và H4 16:00 ngày 23/9/2026 đang chạy dở (close H4 lệch close H1 cùng giờ do hai file tải ở hai thời điểm khác nhau). Dữ liệu nay kết thúc H1 15:00, H4 12:00; D1 (gộp từ H1) kết thúc 22/9/2026. Kết quả D1/H4 không đổi.
   - D1 gộp từ H1 nên 8 ngày (trên 2,092) thiếu vài nến H1, đỉnh/đáy ngày đó có thể lệch rất nhẹ.
   - R trong các bảng chính là chênh giá chia khoảng SL, chưa trừ phí và trượt giá. `full_track.py` xuất thêm bản đã trừ phí 0.04%/chiều (xem "Bảng tổng hợp cuối"); trượt giá vẫn chưa tính.

11. **Vì sao H4 kém (phân tích 26/9/2026)**:
   - **Engine đã kiểm chứng**: viết lại độc lập (EMA/ATR tự tính, vòng lặp riêng) cho cả D1/H4/H1 × 7 mức ATR ra **cùng từng lệnh** (21/21 cấu hình, cùng ngày vào/ra, cùng R; kiểm lại sau khi thêm làm nóng EMA). Với luật cũ, bản viết lại tái tạo đúng số README cũ (50 lệnh, PF 2.44, +41.76R) nên phép tính không sai; cái thay đổi là luật/giả định.
   - **Số H4 cũ (PF 2.44) đã bị thổi phồng bởi giả định khớp lệnh thiếu thực tế** (lệnh chờ bị bỏ qua 1 nến rồi khớp ở mức chờ cũ dù giá đã chạy xa). Phân rã H4 2.0×, dữ liệu 2021-9/2025:

     | Bước áp dụng (theo thứ tự) | Lệnh | Win rate | PF | Kỳ vọng | Max DD |
     |---|---|---|---|---|---|
     | 0. Luật cũ gốc | 50 | 38.0% | 2.44 | +0.835R | -5.00R |
     | 1. + khớp theo giá mở cửa khi gap | 52 | 28.8% | 1.90 | +0.600R | -7.88R |
     | 2. + hủy lệnh chờ khi EMA đảo chiều | 50 | 26.0% | 1.76 | +0.518R | -13.26R |
     | 3. + sửa lệch 1 nến | 56 | 25.0% | 1.61 | +0.398R | -12.07R |
     | 4. + SL trong nến vào lệnh | 56 | 25.0% | 1.61 | +0.398R | -12.07R |
     | 5. + làm nóng EMA 200 nến (hiện tại) | 53 | 26.4% | 1.75 | +0.477R | -10.33R |

   - **Edge tập trung vào vài lệnh thắng lớn** (H4 2.0×, 2021 → 9/2026): tổng +20.37R nhưng 2 lệnh (16/10/2023 +17.2R, 25/2/2024 +18.1R) đã +35R; bỏ lệnh lớn nhất thì tổng chỉ còn +2.28R, bỏ 3 lệnh lớn nhất thì -19.75R. TB thắng +4.22R, TB thua -0.84R, win rate chỉ 22%: chiến lược chỉ có lãi khi bắt được vài đợt trend mạnh.
   - **Theo năm (H4 2.0×)**: 2021 -5.2R (14 lệnh, thắng 3), 2022 -3.9R (thắng 0), 2023 +13.1R, 2024 +16.6R, 2025 +4.6R, 2026 -4.9R (7 lệnh, thắng 0). Thị trường đi ngang/giảm thì bị "cắt" liên tục, chỉ bull run mới bù lại.
   - Kết luận: H4 không sai tính toán mà edge thực sự mỏng và phụ thuộc vài lệnh; các con số đẹp trước đây do giả định khớp lệnh lạc quan.

12. **Làm nóng EMA (thêm 27/9/2026)**: EMA/ATR được khởi tạo từ nến đầu tiên của dữ liệu, nên ở những nến đầu EMA200 còn mang nặng giá trị khởi tạo và tín hiệu "3 EMA xếp hàng" chưa đáng tin. Nay `WARMUP_BARS = 200`: 200 nến đầu của mỗi đoạn dữ liệu chỉ dùng để tính EMA/ATR, không được vào lệnh (áp dụng ở cả 4 script, qua cột `aligned`). Số lệnh bị loại (full track): D1 4 lệnh (200 ngày đầu, đến 20/7/2021), H4 3 lệnh (đến 3/2/2021), H1 2 lệnh (đến 9/1/2021). Các lệnh bị loại đa phần thua nên kết quả tốt lên: full track D1 2.5× PF 2.10→3.01, H4 2.0× PF 1.42→1.53, H1 2.5× PF 2.02→2.01 (gần như không đổi). OOS không đổi (dữ liệu OOS bắt đầu từ 2025-01-01, đã quá 200 nến trước mốc 30/9/2025). Kiểm chứng độc lập 21/21 cấu hình vẫn khớp từng lệnh.

13. **Kiểm chứng độc lập toàn bộ engine (27/9/2026)**: để xác minh code không có lỗi tính toán ẩn, đã viết lại 4 engine (breakout, breakout trong `pullback_test.py`, pullback, hybrid) từ đầu bằng NumPy thuần — tự tính EMA/ATR, vòng lặp riêng, không copy code gốc — rồi so từng lệnh (ngày vào/ra, R) hoặc so giá trị cuối cùng (với Hybrid) với kết quả của script chính.
    - **Breakout** (`backtest_main.py`, `oos_test.py`, `full_track.py`): 21/21 cấu hình (3 khung × 7 mức ATR) khớp từng lệnh.
    - **Breakout và Pullback** (`pullback_test.py`): 24/24 cấu hình (3 khung × 4 mức ATR × 2 kiểu entry) khớp từng lệnh.
    - **Hybrid** (`backtest_main.py`, ATR=2.0×): 3/3 khung khớp giá trị cuối và tổng lãi/lỗ phần margin.
    - **README**: đối chiếu tự động mọi con số trong các bảng chính với kết quả chạy lại — 68/68 dòng khớp.
    - Trong lúc kiểm chứng Hybrid, bản đối chiếu H1 lần đầu lệch ($139,100 so với $142,003) — nguyên nhân là chính kịch bản kiểm tra dùng sai ngưỡng gap (1.5h thay vì 6.0h cho H1, xem lưu ý #10), không phải lỗi trong `backtest_main.py`. Sau khi sửa ngưỡng, cả 3 khung khớp tuyệt đối.
    - Việc kiểm chứng này chỉ xác nhận **code tính đúng theo luật đã định nghĩa**, không xác nhận luật đó khớp với cách khớp lệnh thật trên sàn (trượt giá, thanh khoản) hay kết quả sẽ lặp lại trên dữ liệu tương lai.

14. **Pullback V5 thay cho luật Pullback cũ V1 (28/9/2026)**: luật cũ (V1) lấy nến đầu tiên có low ≤ EMA45 làm nến tín hiệu và giữ mức chờ cố định kể cả khi giá đóng cửa sâu dưới EMA45. Đã thử 5 biến thể trên cùng engine (sau phí 0.04%, 2021 → 9/2026): V1; V2 dời mức chờ xuống nến chạm mới nhất; V3 chỉ nhận nến đầu tiên đóng cửa dưới EMA45; V4 chỉ nhận nến đầu tiên đóng cửa trở lại trên EMA45 sau khi đã đóng cửa dưới; **V5 = V1 cho kiểu "chạm rồi bật" + V4 cho kiểu "cắt xuống rồi cắt lại"**. V3/V4 bỏ lỡ toàn bộ kiểu "chạm rồi bật" — mà đây là nhóm lệnh tốt (BTC H1 2.5×: 87 lệnh PF 1.94; BTC H4: là phần duy nhất có lãi) — nên chọn V5.

    | Cấu hình | V1 (cũ) | V5 (mới) |
    |---|---|---|
    | BTC H1 2.5× | 153 lệnh, PF 1.71, +70.3R, DD -11.5R, OOS PF 1.18 | 159 lệnh, PF 1.84, +80.2R, DD -13.1R, OOS PF 1.15 |
    | BTC H1 2.0× | 159 lệnh, PF 1.59, +71.8R, DD -18.7R | 165 lệnh, PF 1.67, +81.5R, DD -22.8R |
    | Vàng H4 2.0× | 40 lệnh, PF 2.08, +26.4R, DD -6.8R | 40 lệnh, PF 2.50, +30.6R, DD -4.1R |
    | Vàng H4 2.5× | 39 lệnh, PF 2.34, +25.2R, DD -5.9R | 40 lệnh, PF 2.79, +28.3R, DD -3.9R |

    V3 (chỉ đóng cửa dưới EMA45) cho BTC H1 PF cao hơn nữa (2.0–2.05, DD ~-10R, ngoài mẫu PF 1.7–2.3 với 14 lệnh) nhưng kém rõ trên vàng (ngoài mẫu H4 thua cả 2 lệnh), nên không chọn làm mặc định. Đã kiểm chứng: `run_pullback(variant='v1')` vẫn cho đúng số cũ, `variant='v5'` khớp engine độc lập — 48/48 cấu hình (BTC + vàng × D1/H4/H1 × 4 mức ATR × 2 biến thể) khớp từng lệnh. ⚠️ Việc thử nhiều biến thể trên cùng bộ dữ liệu làm tăng nguy cơ overfitting; lợi thế của V5 so với V1 cần được theo dõi thêm ngoài mẫu.

## Kết quả cuối cùng (entry breakout + exit breakdown + lọc EMA9>EMA45>EMA200 + lệnh chờ tự hủy + đã sửa lỗi lệch 1 nến + SL trong nến vào lệnh + làm nóng EMA 200 nến, SL=2xATR, kết thúc 30/9/2025 để so sánh công bằng)

| Khung | Số lệnh | Win rate | Profit Factor | Expectancy | Max DD |
|---|---|---|---|---|---|
| D1 | 10 | 40.0% | **2.12** | +0.576R | -2.71R |
| H4 | 53 | 26.4% | 1.75 | +0.477R | -10.33R |
| H1 | 183 | 24.0% | 1.91 | **+0.620R** | -13.53R |

> Trước khi thêm làm nóng EMA (lưu ý #12): D1 14 lệnh/PF 1.57/+0.319R, H4 56 lệnh/PF 1.61/+0.398R/-11.07R, H1 185 lệnh/PF 1.93/+0.631R/-13.53R.

> Trước khi sửa lỗi lệch 1 nến (lưu ý #8): D1 12 lệnh/PF 2.03/+0.561R, H4 48 lệnh/PF 2.03/+0.651R/-8.77R, H1 164 lệnh/PF 2.19/+0.778R/-12.96R.

> Trước khi thêm luật tự hủy lệnh chờ: D1 13 lệnh/PF 1.78, H4 50 lệnh/PF 2.44/+0.835R/-5.00R, H1 190 lệnh/PF 1.97/+0.633R/-14.01R.

> Kết quả với bộ lọc cũ (chỉ cần giá > EMA200, không yêu cầu EMA45 > EMA200): D1 13 lệnh/PF 1.78 (không đổi), H4 62 lệnh/PF 2.00, H1 260 lệnh/PF 1.74 — H4 và H1 cải thiện rõ rệt với bộ lọc mới, D1 giữ nguyên ở mức ATR mặc định này.

### So sánh chiến lược (vốn ban đầu = 1 BTC, kết thúc 30/9/2025)
| Chiến lược | Giá trị cuối | Nhân vốn | Max DD |
|---|---|---|---|
| DCA hàng tháng | $86,091 | x2.94 | -53.6% |
| Full-capital EMA9/45 (H1, 100% vốn, không giữ BTC nền) | $75,389 | x2.60 | -18.9% |
| Buy & Hold thuần | ~$114,000-114,500 | ~x3.9 | -77% |
| **Hybrid** (giữ 1 BTC + margin vay USDT thêm theo tín hiệu, SL=2xATR, exit breakdown, lọc EMA9>EMA45>EMA200, lệnh chờ tự hủy, đã sửa lệch 1 nến, làm nóng EMA) | | | |
| — D1 | $116,566 | x3.97 | -76.4% |
| — H4 | $122,529 | x4.18 | -83.3% |
| — H1 | **$139,100** | **x4.80** | -80.6% |

> DCA và Full-capital EMA9/45 ở trên chưa được tính lại với luật exit breakdown/bộ lọc EMA mới (không có script tương ứng trong repo) — chỉ Hybrid và bảng số lệnh D1/H4/H1 phía trên đã cập nhật.

> Tất cả các bảng bên dưới đã được tính lại với **luật hiện hành**: bộ lọc EMA9>EMA45>EMA200, exit breakdown, lệnh chờ tự hủy khi EMA đảo chiều, đã sửa lỗi lệch 1 nến, SL trong nến vào lệnh, làm nóng EMA 200 nến (cập nhật 27/9/2026). Max DD tính theo R tích lũy giống `backtest_main.py`.

### Bảng thống kê tổng hợp: Breakout (ATR 1.0–4.0) & Pullback (ATR 1.5–3.0) (in-sample 2021-01-01 → 2025-09-30)

**BREAKOUT** (vào lệnh khi giá phá đỉnh nến tín hiệu cắt lên)

| Khung | ATR (SL) | Số lệnh | Win rate | Profit Factor | Expectancy | Tổng R | Max DD |
|---|---|---|---|---|---|---|---|
| D1 | 1.0× | 10 | 40.0% | 3.63 | **+1.576R** | +15.76R | -3.00R |
| D1 | 1.5× | 10 | 40.0% | 2.42 | +0.851R | +8.51R | -3.00R |
| D1 | 2.0× | 10 | 40.0% | 2.12 | +0.576R | +5.76R | -2.71R |
| D1 | 2.5× | 10 | **50.0%** | **3.83** | +1.045R | +10.45R | -1.57R |
| D1 | 3.0× | 10 | **50.0%** | 3.45 | +0.838R | +8.38R | -1.47R |
| D1 | 3.5× | 10 | **50.0%** | 3.15 | +0.689R | +6.89R | -1.41R |
| D1 | 4.0× | 10 | **50.0%** | 2.99 | +0.588R | +5.88R | **-1.36R** |
| H4 | 1.0× | 56 | 10.7% | 0.50 | -0.444R | -24.89R | -34.55R |
| H4 | 1.5× | 54 | 22.2% | 1.39 | +0.284R | +15.36R | -10.93R |
| H4 | 2.0× | 53 | 26.4% | **1.75** | **+0.477R** | +25.27R | -10.33R |
| H4 | 2.5× | 52 | 28.8% | **1.75** | +0.419R | +21.81R | -10.27R |
| H4 | 3.0× | 51 | **31.4%** | 1.71 | +0.347R | +17.71R | -8.12R |
| H4 | 3.5× | 51 | **31.4%** | 1.62 | +0.277R | +14.11R | -7.32R |
| H4 | 4.0× | 51 | **31.4%** | 1.61 | +0.239R | +12.17R | **-7.05R** |
| H1 | 1.0× | 191 | 14.1% | 2.08 | **+0.915R** | +174.84R | -24.81R |
| H1 | 1.5× | 187 | 22.5% | 2.02 | +0.751R | +140.42R | -15.17R |
| H1 | 2.0× | 183 | 24.0% | 1.91 | +0.620R | +113.41R | -13.53R |
| H1 | 2.5× | 177 | 27.7% | **2.13** | +0.670R | +118.64R | -10.47R |
| H1 | 3.0× | 175 | **29.1%** | 2.09 | +0.575R | +100.59R | **-9.05R** |
| H1 | 3.5× | 175 | **29.1%** | 1.93 | +0.454R | +79.44R | -9.64R |
| H1 | 4.0× | 175 | **29.1%** | 1.84 | +0.377R | +65.98R | -9.07R |

(H1 2.5× có PF cao nhất 2.13; 1.0× có expectancy cao nhất nhưng DD sâu nhất -25R.)

**PULLBACK V5** (chờ giá hồi về EMA45 — chạm rồi bật, hoặc cắt xuống rồi cắt lại — rồi vào khi phá đỉnh nến tín hiệu, `pullback_test.py`)

| Khung | ATR (SL) | Số lệnh | Win rate | Profit Factor | Expectancy | Tổng R | Max DD |
|---|---|---|---|---|---|---|---|
| D1 | 1.5× | 7 | 14.3% | 1.35 | +0.300R | +2.10R | -4.00R |
| D1 | 2.0× | 7 | 28.6% | 2.94 | **+1.385R** | +9.70R | **-2.00R** |
| D1 | 2.5× | 7 | 28.6% | 2.87 | +1.095R | +7.67R | **-2.00R** |
| D1 | 3.0× | 7 | **42.9%** | **3.50** | +1.039R | +7.27R | **-2.00R** |
| H4 | 1.5× | 39 | 15.4% | 0.68 | -0.247R | -9.64R | -14.95R |
| H4 | 2.0× | 39 | 15.4% | 0.55 | -0.323R | -12.60R | -14.33R |
| H4 | 2.5× | 38 | **18.4%** | **1.20** | **+0.124R** | +4.71R | -11.51R |
| H4 | 3.0× | 38 | **18.4%** | 1.11 | +0.063R | +2.39R | **-9.96R** |
| H1 | 1.5× | 140 | 19.3% | 1.35 | +0.274R | +38.35R | -24.97R |
| H1 | 2.0× | 139 | 23.7% | 2.09 | **+0.736R** | +102.34R | -13.60R |
| H1 | 2.5× | 136 | 25.0% | **2.14** | +0.648R | +88.19R | -8.93R |
| H1 | 3.0× | 135 | **25.9%** | 2.03 | +0.518R | +69.90R | **-8.87R** |

### Cấu hình tối ưu theo từng khung thời gian (in-sample)

| Khung | Entry | ATR (SL) | Win rate | Profit Factor | Expectancy | Max DD |
|---|---|---|---|---|---|---|
| D1 | Breakout | 4.0× | 50.0% | 2.99 | +0.588R | **-1.36R** |
| **D1** | **Breakout** | 2.5× | 50.0% | **3.83** | **+1.045R** | -1.57R |
| D1 | Pullback V5 | 3.0× | 42.9% | 3.50 | +1.039R | -2.00R |
| **H4** | **Breakout** | 2.0× | 26.4% | **1.75** | **+0.477R** | -10.33R |
| H4 | Breakout | 3.0× | 31.4% | 1.71 | +0.347R | **-8.12R** |
| H4 | Pullback V5 | 2.5× | 18.4% | 1.20 | +0.124R | -11.51R |
| **H1** | **Breakout** | 2.5× | 27.7% | 2.13 | **+0.670R** | -10.47R |
| H1 | Pullback V5 | 2.5× | 25.0% | **2.14** | +0.648R | -8.93R |
| H1 | Pullback V5 | 3.0× | 25.9% | 2.03 | +0.518R | **-8.87R** |

**Nhận xét từng khung:**
- **D1**: Breakout 2.5× (PF 3.83, 10 lệnh) và Pullback V5 3.0× (PF 3.50, 7 lệnh) đẹp trên giấy — nhưng chỉ 7–10 lệnh/~5 năm, độ tin cậy rất thấp.
- **H4**: sau khi sửa lỗi lệch nến, edge H4 yếu đi rõ rệt (PF chỉ 1.39–1.75 ở ATR 1.5–4.0×, DD -7.1 đến -10.9R; 1.0× lỗ nặng). Breakout vẫn thắng Pullback; **không nên dùng Pullback cho H4** (V5 lỗ ròng ở 1.5–2.0×, chỉ PF 1.1–1.2 ở 2.5–3.0×). PF cao nhất ở 2.0–2.5× (1.75); 3.0× có DD nhẹ hơn (-8.12R) với PF 1.71.
- **H1**: khung có edge mạnh nhất. In-sample, Pullback V5 2.0–3.0× (PF 2.03–2.14, DD -8.9 đến -13.6R) **ngang Breakout** (PF 1.91–2.13) về PF và nhẹ hơn về DD, nhưng ít lệnh hơn (~136 so với ~177). V5 1.5× yếu (PF 1.35).

**Tổng kết**: in-sample, **Breakout tốt hơn Pullback ở H4**; ở H1 Pullback V5 2.0–3.0× ngang Breakout về PF (xem ngoài mẫu và tính gộp bên dưới — Breakout vẫn bền hơn); ở D1 mẫu quá nhỏ để tin.

> ⚠️ **Cảnh báo overfitting**: các bảng trên là kết quả dò 11 tổ hợp (7 mức ATR breakout + 4 mức ATR pullback) trên mỗi khung, cùng 1 bộ dữ liệu lịch sử duy nhất — càng thử nhiều tham số, càng dễ "chọn được" con số đẹp chỉ vì khớp ngẫu nhiên với quá khứ, đặc biệt với D1 (mẫu nhỏ). Xem mục "Validation out-of-sample" ngay bên dưới.

### Validation out-of-sample (dữ liệu thật sau 30/9/2025)

Chạy `scripts/oos_test.py`: dùng dữ liệu Binance API liên tục (không gap) từ 2025-01-01 làm warm-up tính EMA/ATR, nhưng **chỉ tính thống kê cho các lệnh vào SAU 30/9/2025** (dữ liệu đến 23/9/2026) — đây là dữ liệu chiến lược chưa từng "nhìn thấy" khi các bảng tối ưu ở trên được tính.

**Breakout, tất cả mức ATR:**

| Khung | ATR | Số lệnh OOS | Win rate | PF | Expectancy | Tổng R |
|---|---|---|---|---|---|---|
| D1 | 1.0–4.0× | 1 | 0% | 0.00 | -1.000R | -1.00R |
| H4 | 1.0× | 7 | 0% | 0.00 | -0.878R | -6.15R |
| H4 | 1.5× | 7 | 0% | 0.00 | -0.871R | -6.10R |
| H4 | 2.0× | 7 | 0% | 0.00 | -0.701R | -4.91R |
| H4 | 2.5× | 7 | 0% | 0.00 | -0.675R | -4.73R |
| H4 | 3.0× | 7 | 0% | 0.00 | -0.658R | -4.61R |
| H4 | 3.5× | 7 | 0% | 0.00 | -0.596R | -4.18R |
| H4 | 4.0× | 7 | 0% | 0.00 | -0.527R | -3.69R |
| H1 | **1.0×** | 32 | 21.9% | **1.52** | **+0.408R** | **+13.05R** |
| H1 | 1.5× | 32 | 31.3% | 1.44 | +0.301R | +9.64R |
| H1 | 2.0× | 30 | 36.7% | 1.24 | +0.145R | +4.35R |
| H1 | 2.5× | 28 | 39.3% | 1.18 | +0.103R | +2.87R |
| H1 | 3.0× | 28 | 39.3% | 1.02 | +0.008R | +0.22R |
| H1 | 3.5× | 28 | 39.3% | 0.96 | -0.018R | -0.50R |
| H1 | 4.0× | 28 | 39.3% | 0.96 | -0.018R | -0.50R |

**Pullback V5, tất cả mức ATR** (chạy `scripts/oos_pullback_test.py` — cùng luật/warm-up với `oos_test.py`; V5 khớp engine độc lập 48/48 cấu hình, lưu ý #14):

| Khung | ATR | Số lệnh OOS | Win rate | PF | Expectancy | Tổng R |
|---|---|---|---|---|---|---|
| D1 | 1.5–3.0× | 0 | – | – | – | – |
| H4 | 1.5× | 2 | 50.0% | 0.53 | -0.237R | -0.47R |
| H4 | 2.0× | 2 | 50.0% | 0.44 | -0.247R | -0.49R |
| H4 | 2.5× | 2 | 50.0% | 0.44 | -0.197R | -0.39R |
| H4 | 3.0× | 2 | 50.0% | 0.44 | -0.164R | -0.33R |
| H1 | 1.5× | 26 | 19.2% | 0.57 | -0.335R | -8.70R |
| H1 | 2.0× | 26 | 23.1% | 0.55 | -0.324R | -8.43R |
| H1 | 2.5× | 23 | 39.1% | 1.15 | +0.074R | +1.70R |
| H1 | 3.0× | 23 | 39.1% | 0.99 | -0.004R | -0.08R |

**So sánh Breakout vs Pullback ngoài mẫu:**
- **D1**: Pullback V5 không có lệnh nào vào sau 30/9/2025 (chỉ 7 lệnh cả giai đoạn). Breakout có đúng 1 lệnh, thua.
- **H4**: cả hai đều lỗ. Breakout thua cả 7 lệnh; Pullback V5 chỉ có 2 lệnh (thắng 1, thua 1) nhưng vẫn lỗ ròng ở mọi mức ATR.
- **H1**: **Breakout bền hơn** — PF 0.96–1.52 tùy ATR, tốt nhất ở ATR thấp. Pullback V5 chỉ có lãi ở 2.5× (PF 1.15), hòa vốn ở 3.0× (PF 0.99) và lỗ nặng ở 1.5–2.0× (PF 0.55–0.57) — ngược hẳn với in-sample, nơi V5 2.0× có PF 2.09. Cấu hình Pullback tốt in-sample mất phần lớn edge trên dữ liệu mới, rõ hơn Breakout.

**Kết luận Breakout vs Pullback ngoài mẫu**: Breakout **giữ được edge tốt hơn ở ngoài mẫu**. Pullback V5 H1 chỉ còn lãi nhẹ ở 2.5×, còn Breakout H1 vẫn có PF 1.0–1.5 ở hầu hết mức ATR. Khuyến nghị dùng Breakout làm chiến lược chính cho BTC.

**Full track record cả 3 khung (2021-01-01 → 23/9/2026, gộp in-sample + out-of-sample, breakout, luật hiện hành):**

Chạy `scripts/full_track.py` để tính lại bảng này (kết quả lưu vào `results/full_track_summary.csv`). Dữ liệu: H1 = `h1_combined_2021_now.csv`; H4 = `h4_full.csv` (liền mạch đến 23/9/2026 12:00); D1 = resample từ H1 gộp (đến 22/9/2026, bỏ ngày 23 chưa đủ nến).

| Khung | ATR | Số lệnh | Win rate | PF | Expectancy | Tổng R | Max DD |
|---|---|---|---|---|---|---|---|
| D1 | 1.0× | 11 | 36.4% | **3.11** | **+1.342R** | +14.76R | -3.00R |
| D1 | 1.5× | 11 | 36.4% | 2.07 | +0.682R | +7.51R | -3.00R |
| D1 | 2.0× | 11 | 36.4% | 1.78 | +0.432R | +4.76R | -2.71R |
| D1 | 2.5× | 11 | **45.5%** | 3.01 | +0.859R | +9.45R | -2.00R |
| D1 | 3.0× | 11 | **45.5%** | 2.67 | +0.670R | +7.38R | -2.00R |
| D1 | 3.5× | 11 | **45.5%** | 2.40 | +0.536R | +5.89R | -2.00R |
| D1 | 4.0× | 11 | **45.5%** | 2.23 | +0.444R | +4.88R | **-1.90R** |
| H4 | 1.0× | 63 | 9.5% | 0.44 | -0.493R | -31.04R | -34.55R |
| H4 | 1.5× | 61 | 19.7% | 1.20 | +0.152R | +9.26R | -10.93R |
| H4 | 2.0× | 60 | 23.3% | **1.53** | **+0.339R** | +20.37R | -10.33R |
| H4 | 2.5× | 59 | 25.4% | 1.51 | +0.290R | +17.09R | -10.27R |
| H4 | 3.0× | 58 | **27.6%** | 1.44 | +0.226R | +13.10R | -8.12R |
| H4 | 3.5× | 58 | **27.6%** | 1.37 | +0.171R | +9.94R | -7.32R |
| H4 | 4.0× | 58 | **27.6%** | 1.36 | +0.146R | +8.48R | **-7.05R** |
| H1 | 1.0× | 223 | 15.2% | **2.01** | **+0.843R** | +187.89R | -28.81R |
| H1 | 1.5× | 219 | 23.7% | 1.94 | +0.685R | +150.06R | -17.06R |
| H1 | 2.0× | 213 | 25.8% | 1.83 | +0.553R | +117.76R | -17.19R |
| H1 | 2.5× | 205 | 29.3% | **2.01** | +0.593R | +121.51R | -14.00R |
| H1 | 3.0× | 203 | **30.5%** | 1.94 | +0.497R | +100.81R | -11.54R |
| H1 | 3.5× | 203 | **30.5%** | 1.79 | +0.389R | +78.94R | -10.75R |
| H1 | 4.0× | 203 | **30.5%** | 1.72 | +0.323R | +65.48R | **-9.76R** |

**Tóm tắt full track record:**

| Khung | ATR cân bằng nhất | Win rate | PF | Max DD | Nhận xét |
|---|---|---|---|---|---|
| D1 | 2.5× | 45.5% | 3.01 | -2.00R | PF đẹp nhưng chỉ 11 lệnh/gần 6 năm, độ tin cậy thấp |
| H4 | 2.0–3.0× | 23–28% | 1.44–1.53 | -8.1 đến -10.3R | Yếu nhất — PF thấp, DD lớn so với tổng R |
| H1 | **2.5×** | 29.3% | **2.01** | -14.00R | Tốt nhất — mẫu lớn (205 lệnh), PF ổn định ở mọi mức ATR |

**Nhận xét:**
- **D1**: chỉ 1 lệnh trong ~1 năm dữ liệu mới (thua) — mẫu quá nhỏ để kết luận.
- **H4 lỗ ở mọi mức ATR out-of-sample** (7 lệnh, không lệnh nào thắng). Kết hợp với edge in-sample đã yếu đi sau khi sửa lỗi lệch nến (PF ≤ 1.65), hiện **không có bằng chứng H4 còn edge**.
- **H1 vẫn lãi out-of-sample ở ATR 1.0–3.0×** (PF 1.02–1.52), hòa/lỗ nhẹ ở 3.5–4.0×. ATR càng rộng thì OOS càng yếu, ngược với in-sample (nơi 2.5–4.0× có DD tốt nhất). Đây vẫn là dấu hiệu tham số "tối ưu" in-sample không hoàn toàn tổng quát hóa.
- Xét full track record (2021 → 9/2026), H1 là khung tốt nhất và H4 yếu nhất (PF chỉ 0.44–1.53); H1 2.5× là mức cân bằng tốt nhất (PF 2.01, DD -14.00R); 1.0× lợi nhuận cao nhất nhưng DD rất sâu (-29R); 1.5× là điểm giữa (PF 1.94, DD -17R, OOS PF 1.44).

**Kết luận validation**: với luật hiện hành, **H1 là khung duy nhất còn giữ edge trên dữ liệu chưa từng thấy** (28–32 lệnh OOS), còn **H4 và D1 không thể hiện lợi thế ngoài mẫu**. Nếu giao dịch thật, nên ưu tiên **H1 + Breakout + 1.5–2.5×ATR** (1.5× nếu tin vào giai đoạn gần đây, 2.5× nếu ưu tiên DD lịch sử), và tiếp tục chạy lại `oos_test.py` định kỳ khi có thêm dữ liệu.

### So sánh Breakout vs Pullback V5 theo từng khung (2021-01-01 → 23/9/2026)

Các cột lệnh, win rate, PF, kỳ vọng, tổng R, Max DD, R/DD là toàn bộ 2021 → 9/2026, **đã trừ phí 0.04%/chiều** (Breakout: `full_track_summary.csv`; Pullback V5: `run_pullback` của `asset_test.py`, khớp engine độc lập 48/48). Cột cuối là PF chưa trừ phí: in-sample (2021 → 9/2025) → ngoài mẫu (lệnh vào sau 30/9/2025). **In đậm** = bên có lợi thế ở chỉ số đó. Với H4/D1, SL trong nến vào lệnh xử lý bằng nến H1 như lưu ý #9.

#### H1

| ATR | Chiến lược | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | PF 2021–2025 → ngoài mẫu |
|---|---|---|---|---|---|---|---|---|---|
| 1.5× | Breakout | **219** | **22.8%** | **1.72** | **+0.584R** | **+127.9R** | **-19.98R** | **6.40** | **2.02** → **1.44** |
| 1.5× | Pullback V5 | 166 | 18.7% | 1.09 | +0.079R | +13.1R | -30.30R | 0.43 | 1.35 → 0.57 |
| 2.0× | Breakout | **213** | **24.9%** | 1.66 | +0.477R | **+101.6R** | **-19.38R** | **5.24** | 1.91 → **1.23** |
| 2.0× | Pullback V5 | 165 | 23.0% | **1.67** | **+0.494R** | +81.5R | -22.79R | 3.58 | **2.09** → 0.55 |
| 2.5× | Breakout | **205** | **28.3%** | **1.84** | **+0.533R** | **+109.2R** | -15.28R | **7.15** | 2.13 → **1.18** |
| 2.5× | Pullback V5 | 159 | 26.4% | 1.84 | +0.504R | +80.2R | **-13.10R** | 6.12 | **2.14** → 1.15 |
| 3.0× | Breakout | **203** | **29.6%** | **1.79** | **+0.447R** | **+90.7R** | **-12.54R** | **7.23** | **2.09** → **1.01** |
| 3.0× | Pullback V5 | 158 | 27.2% | 1.73 | +0.391R | +61.8R | -12.77R | 4.84 | 2.03 → 0.99 |

- **Ở 2.5× hai bên có cùng PF (1.84)**: Breakout nhiều lệnh hơn (205 so với 159), tổng R cao hơn (+109R so với +80R), R/DD tốt hơn (7.15 so với 6.12); Pullback V5 có DD nhẹ hơn (-13.1R so với -15.3R).
- **Ở ATR thấp (1.5–2.0×) Pullback V5 kém hẳn** và lỗ ngoài mẫu (PF 0.55–0.57); Breakout vẫn lãi ngoài mẫu ở mọi mức này. Breakout bền hơn.

#### H4

| ATR | Chiến lược | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | PF 2021–2025 → ngoài mẫu |
|---|---|---|---|---|---|---|---|---|---|
| 1.5× | Breakout | **61** | **19.7%** | **1.14** | **+0.109R** | **+6.6R** | **-11.78R** | **0.56** | **1.39** → 0.00 (0/7) |
| 1.5× | Pullback V5 | 41 | 17.1% | 0.64 | -0.287R | -11.8R | -16.52R | -0.71 | 0.68 → **0.53 (2 lệnh)** |
| 2.0× | Breakout | **60** | **21.7%** | **1.46** | **+0.307R** | **+18.4R** | **-10.77R** | **1.71** | **1.75** → 0.00 (0/7) |
| 2.0× | Pullback V5 | 41 | 17.1% | 0.52 | -0.350R | -14.3R | -15.09R | -0.95 | 0.55 → **0.44 (2 lệnh)** |
| 2.5× | Breakout | **59** | **23.7%** | **1.45** | **+0.264R** | **+15.6R** | **-10.63R** | **1.46** | **1.75** → 0.00 (0/7) |
| 2.5× | Pullback V5 | 40 | 20.0% | 1.13 | +0.084R | +3.3R | -12.10R | 0.28 | 1.20 → **0.44 (2 lệnh)** |
| 3.0× | Breakout | **58** | **25.9%** | **1.39** | **+0.204R** | **+11.8R** | **-8.37R** | **1.41** | **1.71** → 0.00 (0/7) |
| 3.0× | Pullback V5 | 40 | 20.0% | 1.06 | +0.031R | +1.3R | -10.45R | 0.12 | 1.11 → **0.44 (2 lệnh)** |

- **Breakout thắng gần như mọi chỉ số**; Pullback V5 lỗ ròng ở 1.5–2.0× và gần hòa vốn ở 2.5–3.0× (PF sau phí 1.06–1.13).
- **Ngoài mẫu cả hai đều lỗ**; Pullback lỗ ít hơn chỉ vì có 2 lệnh so với 7. Không dùng H4, nhất là Pullback H4.

#### D1

| ATR | Chiến lược | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | PF 2021–2025 → ngoài mẫu |
|---|---|---|---|---|---|---|---|---|---|
| 1.5× | Breakout | **11** | **36.4%** | **2.02** | **+0.665R** | **+7.3R** | **-3.04R** | **2.40** | **2.42** → **0.00 (1 lệnh)** |
| 1.5× | Pullback V5 | 7 | 14.3% | 1.33 | +0.283R | +2.0R | -4.07R | 0.49 | 1.35 → không có lệnh |
| 2.0× | Breakout | **11** | **36.4%** | 1.74 | +0.419R | +4.6R | -2.74R | 1.68 | 2.12 → **0.00 (1 lệnh)** |
| 2.0× | Pullback V5 | 7 | 28.6% | **2.90** | **+1.373R** | **+9.6R** | **-2.02R** | **4.75** | **2.94** → không có lệnh |
| 2.5× | Breakout | **11** | **45.5%** | **2.96** | +0.848R | **+9.3R** | -2.03R | **4.59** | **3.83** → **0.00 (1 lệnh)** |
| 2.5× | Pullback V5 | 7 | 28.6% | 2.84 | **+1.085R** | +7.6R | **-2.02R** | 3.76 | 2.87 → không có lệnh |
| 3.0× | Breakout | **11** | **45.5%** | 2.63 | +0.661R | **+7.3R** | -2.03R | **3.59** | 3.45 → **0.00 (1 lệnh)** |
| 3.0× | Pullback V5 | 7 | 42.9% | **3.46** | **+1.030R** | +7.2R | **-2.02R** | 3.58 | **3.50** → không có lệnh |

- Pullback V5 có PF 2.8–3.5 ở 2.0–3.0× nhưng chỉ **7 lệnh** trong gần 6 năm, tất cả trước 30/9/2025 — **chưa từng được kiểm tra ngoài mẫu**. Breakout có 11 lệnh. D1 nói chung không đủ dữ liệu để dùng.

### Bảng thống kê đầy đủ khung H4 — BTC/USDT (cập nhật 3/10/2026)

Dữ liệu tải mới từ Binance (`data/btc_h4_binance.csv`, `data/btc_h1_binance.csv`, 2021-01-01 → 2026-10-02 12:00 UTC; trùng khớp dữ liệu cũ đến 23/9/2026, lệch tối đa 0.01). Chạy bằng `cd scripts` rồi `python h4_report.py ../data/btc_h1_binance.csv ../data/btc_h4_binance.csv` (dùng nguyên các hàm của `asset_test.py`, SL trong nến vào lệnh xử lý bằng nến H1, làm nóng EMA 200 nến), kết quả ở `results/h4_report.csv`. **Mọi số đã trừ phí 0.04%/chiều** (trừ cột cuối: phí 0.1%/chiều). Vốn $1,000 rủi ro 1%/lệnh, lãi kép. Ngoài mẫu = lệnh vào từ 1/10/2025. Lệnh đang mở (nếu có) chưa tính.

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | Chuỗi thua dài nhất | Lệnh thắng lớn nhất | Vốn $1,000 → | DD vốn | PF trong mẫu → ngoài mẫu | PF phí 0.1% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Breakout | 1.0× | 64 | 10.9% | 0.44 | -0.521R | -33.3R | -38.27R | -0.87 | 21 | +8.3R | $710 (-29.0%) | -32.3% | 0.46 → 0.25 (1/8 thắng) | 0.39 |
| Breakout | 1.5× | 62 | 21.0% | 1.16 | +0.125R | +7.8R | -11.78R | 0.66 | 12 | +22.9R | $1,047 (+4.7%) | -11.2% | 1.32 → 0.17 (1/8 thắng) | 1.07 |
| **Breakout** | **2.0×** | 61 | 23.0% | 1.48 | +0.316R | +19.3R | -10.77R | 1.79 | 12 | +18.0R | $1,173 (+17.3%) | -10.3% | 1.68 → 0.16 (1/8 thắng) | 1.39 |
| Breakout | 2.5× | 60 | 25.0% | 1.47 | +0.271R | +16.2R | -10.63R | 1.53 | 12 | +14.4R | $1,150 (+15.0%) | -10.2% | 1.69 → 0.14 (1/8 thắng) | 1.38 |
| Breakout | 3.0× | 59 | 27.1% | 1.41 | +0.210R | +12.4R | -8.37R | 1.48 | 9 | +12.0R | $1,114 (+11.4%) | -8.1% | 1.65 → 0.12 (1/8 thắng) | 1.33 |
| Breakout | 3.5× | 59 | 27.1% | 1.34 | +0.158R | +9.3R | -7.64R | 1.22 | 9 | +10.3R | $1,085 (+8.5%) | -7.4% | 1.57 → 0.11 (1/8 thắng) | 1.27 |
| Breakout | 4.0× | 59 | 27.1% | 1.33 | +0.135R | +8.0R | -7.34R | 1.08 | 9 | +9.0R | $1,073 (+7.3%) | -7.1% | 1.56 → 0.11 (1/8 thắng) | 1.26 |
| Pullback V5 | 1.5× | 41 | 17.1% | 0.64 | -0.287R | -11.8R | -16.52R | -0.71 | 16 | +7.4R | $883 (-11.7%) | -15.3% | 0.65 → 0.45 (1/2 thắng) | 0.59 |
| Pullback V5 | 2.0× | 41 | 17.1% | 0.52 | -0.350R | -14.3R | -15.09R | -0.95 | 16 | +5.5R | $863 (-13.7%) | -14.1% | 0.53 → 0.38 (1/2 thắng) | 0.48 |
| Pullback V5 | 2.5× | 40 | 20.0% | 1.13 | +0.084R | +3.3R | -12.10R | 0.28 | 15 | +15.7R | $1,019 (+1.9%) | -11.4% | 1.16 → 0.38 (1/2 thắng) | 1.07 |
| Pullback V5 | 3.0× | 40 | 20.0% | 1.06 | +0.031R | +1.3R | -10.45R | 0.12 | 15 | +13.1R | $1,002 (+0.2%) | -10.0% | 1.08 → 0.38 (1/2 thắng) | 1.00 |

Buy & Hold cùng giai đoạn: 29,278 → 85,326 (x2.91), Max DD -77.0%.

- **ATR tối ưu cho H4 là 2.0×** (R/DD 1.79 cao nhất, PF 1.48, +19.3R, $1,000 → $1,173 sau gần 6 năm, DD vốn -10.3%); 2.5–3.0× gần tương đương. 1.0× lỗ nặng.
- **Pullback V5 không có lợi thế ở H4**: lỗ ở 1.5–2.0×, gần hòa vốn ở 2.5–3.0×.
- **Ngoài mẫu vẫn lỗ ở mọi cấu hình**: Breakout chỉ thắng 1/8 lệnh từ 1/10/2025 (PF 0.11–0.25), Pullback V5 1/2 lệnh. Lãi toàn giai đoạn phụ thuộc vài lệnh lớn (lệnh thắng lớn nhất +9 đến +23R, chuỗi thua dài 9–12 lệnh với Breakout).
- So với bảng cũ (đến 23/9/2026) Breakout có thêm 1 lệnh mới (thắng) ở mọi mức ATR; Pullback V5 không đổi. Kết luận không đổi: **BTC H4 không nên dùng**, H1 Breakout 2.5× vẫn là cấu hình tốt nhất.

#### Tổng kết Breakout vs Pullback V5 (BTC)

| Khung | Bên thắng | Lý do | Nên dùng? |
|---|---|---|---|
| **H1** | **Breakout** | Cùng PF ở 2.5× nhưng tổng R cao hơn ~35%, nhiều lệnh hơn, bền hơn ngoài mẫu ở mọi ATR | **Có — Breakout 2.5×** (Pullback V5 2.5× là phương án phụ, DD nhẹ hơn) |
| H4 | Breakout | Pullback V5 gần như không lãi; cả hai lỗ ngoài mẫu | Không |
| D1 | Không kết luận | 7–11 lệnh, Pullback chưa kiểm tra ngoài mẫu | Không (thiếu dữ liệu) |

### Bảng tổng hợp cuối: ATR tối ưu cho H1/H4/D1 (2021-01-01 → 23/9/2026)

Số liệu từ `scripts/full_track.py` (cột chưa trừ phí và đã trừ phí 0.04%/chiều đều có trong `results/full_track_summary.csv`). **ATR tối ưu = mức có Tổng R / |Max DD| (R/DD) cao nhất sau khi trừ phí**, ưu tiên mức ổn định khi phí đổi. Phí quy ra R = phí × (giá vào + giá ra) / khoảng SL, nên SL càng hẹp càng mất nhiều R mỗi lệnh (H1 1.0×: -0.152R/lệnh, 2.5×: -0.060R/lệnh, 4.0×: -0.037R/lệnh).

| Khung | ATR tối ưu | Số lệnh | Win rate | PF | Expectancy | Max DD | R/DD |
|---|---|---|---|---|---|---|---|
| **H1** | **2.5×** | 205 | 28.3% | 1.84 | +0.533R | -15.28R | 7.15 |
| **H4** | **2.0×** | 60 | 21.7% | 1.46 | +0.307R | -10.77R | 1.71 |
| **D1** | **2.5×** | 11 | 45.5% | 2.96 | +0.848R | -2.03R | 4.59 |

(Số liệu trên đã trừ phí. Chưa trừ phí: H1 2.5× PF 2.01/+0.593R/-14.00R; H4 2.0× PF 1.53/+0.339R/-10.33R; D1 2.5× PF 3.01/+0.859R/-2.00R.)

- **H1 2.5×** hơi kém 3.0× về R/DD sau phí (7.15 so với 7.23) nhưng còn lãi ở giai đoạn ngoài mẫu (PF 1.18, trong khi 3.0× gần hòa vốn PF 1.01); khi phí cao (0.1%/chiều) 2.5× và 3.0× ngang nhau (R/DD 5.28), còn 1.5× chỉ 3.79. H1 1.5× dẫn đầu khi chưa trừ phí (R/DD 8.80) nhưng tụt còn 6.40 sau phí.
- **H4 2.0×** có R/DD sau phí tốt nhất (1.71; 3.0× là 1.41) nhưng vẫn chỉ lãi mỏng và phụ thuộc vài lệnh thắng lớn (xem lưu ý #11); 1.0× lỗ nặng. Trước khi thêm làm nóng EMA thì 3.0× nhỉnh hơn — thứ hạng giữa 2.0× và 3.0× không ổn định.
- **D1 2.5×**: R/DD cao nhất thực ra là 1.0× (4.72 sau phí, gần bằng 2.5×), chọn 2.5× vì win rate cao hơn, DD thấp hơn; mẫu chỉ 11 lệnh nên độ tin cậy thấp.

## Vàng (PAXG/USDT) — áp dụng cùng chiến lược (27/9/2026)

Dữ liệu: PAXG/USDT trên Binance (mỗi token bảo chứng bằng 1 ounce vàng), 2021-01-01 → 2026-09-27, tải bằng `scripts/download_binance.py`; backtest bằng `scripts/asset_test.py` (dùng nguyên các hàm `prep`/`run_breakout`/`run_pullback` của `oos_pullback_test.py`, đã chạy thử trên dữ liệu BTC và khớp 21/21 cấu hình với `full_track_summary.csv`). Luật giống hệt BTC (lọc 3 EMA, hủy lệnh chờ, sửa lệch nến, SL trong nến vào lệnh bằng nến H1 cho H4/D1, làm nóng EMA 200 nến). Tách giai đoạn: lệnh vào trước 1/10/2025 = in-sample, từ 1/10/2025 = ngoài mẫu (cùng mốc với BTC, nhưng chạy liên tục trên một file thay vì warm-up riêng từ 2025-01-01). Kết quả đầy đủ: `results/paxg_summary.csv`.

**Kiểm tra dữ liệu**: không trùng timestamp, không NaN, không nến OHLC vô lý; H4 khớp 100% với H1 gộp lại (12,564 nến). H1 có đúng 7 chỗ thiếu nến, **trùng ngày giờ với 7 chỗ thiếu của BTC** — xác nhận đó là lúc Binance bảo trì toàn sàn (lưu ý #10). **Thanh khoản mỏng**: trung vị khối lượng mỗi giờ chỉ ~$46k–$126k trong 2021–2024, ~$410k–$610k trong 2025–2026, nên trượt giá thực tế sẽ lớn hơn BTC nhiều.

Các bảng: lệnh, win rate, PF, kỳ vọng, Max DD là toàn giai đoạn **đã trừ phí 0.04%/chiều**; cột "PF phí 0.1%" là mức phí spot; cột cuối là PF chưa trừ phí. **In đậm** = tốt nhất trong khung.

#### PAXG H4

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Max DD | PF phí 0.1% | PF in-sample → ngoài mẫu (lệnh OOS) |
|---|---|---|---|---|---|---|---|---|
| Breakout | 1.0× | 61 | 18.0% | 1.04 | +0.033R | -29.93R | 0.83 | 1.12 → 2.14 (8) |
| Breakout | 1.5× | 58 | 31.0% | 1.64 | +0.413R | -13.20R | 1.36 | 1.47 → 5.15 (8) |
| Breakout | 2.0× | 56 | 37.5% | 2.51 | +0.740R | -6.49R | 2.13 | 2.47 → 6.23 (8) |
| Breakout | 2.5× | 55 | 38.2% | 2.43 | +0.589R | -4.62R | 2.08 | 2.37 → 6.23 (8) |
| Breakout | 3.0× | 54 | 38.9% | 2.38 | +0.494R | -4.19R | 2.05 | 2.31 → 6.23 (8) |
| Breakout | 3.5× | 52 | 40.4% | 2.61 | +0.458R | -3.16R | 2.23 | 2.56 → 6.23 (8) |
| Breakout | 4.0× | 52 | 40.4% | 2.53 | +0.393R | **-2.89R** | 2.17 | 2.47 → 6.23 (8) |
| Pullback V5 | 1.5× | 41 | 34.1% | 1.77 | +0.503R | -8.26R | 1.48 | 1.79 → 3.18 (6) |
| Pullback V5 | 2.0× | 40 | 40.0% | 2.50 | **+0.766R** | -4.13R | 2.14 | 2.86 → 2.50 (6) |
| Pullback V5 | 2.5× | 40 | **45.0%** | **2.79** | +0.707R | -3.90R | **2.39** | 3.32 → 2.35 (6) |
| Pullback V5 | 3.0× | 40 | **45.0%** | 2.72 | +0.581R | -3.69R | 2.34 | 3.32 → 2.09 (6) |

#### PAXG H1

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Max DD | PF phí 0.1% | PF in-sample → ngoài mẫu (lệnh OOS) |
|---|---|---|---|---|---|---|---|---|
| Breakout | 1.0× | 246 | 17.5% | 1.09 | +0.095R | -100.19R | 0.73 | 0.94 → 5.47 (33) |
| Breakout | 1.5× | 237 | 24.1% | 1.23 | +0.203R | -65.30R | 0.89 | 1.14 → 4.66 (31) |
| Breakout | 2.0× | 226 | 27.4% | 1.19 | +0.144R | -52.84R | 0.89 | 1.10 → 3.87 (31) |
| Breakout | 2.5× | 220 | 30.5% | 1.27 | +0.161R | -39.25R | 0.95 | 1.17 → 3.91 (31) |
| Breakout | 3.0× | 217 | 32.7% | 1.42 | +0.210R | -32.37R | 1.08 | 1.27 → 4.77 (30) |
| Breakout | 3.5× | 217 | 33.6% | 1.44 | +0.189R | -24.42R | 1.09 | 1.29 → 4.88 (30) |
| Breakout | 4.0× | 214 | **35.0%** | **1.53** | +0.196R | **-19.32R** | **1.17** | 1.36 → 5.53 (30) |
| Pullback V5 | 1.5× | 192 | 18.2% | 1.42 | **+0.369R** | -75.71R | 1.04 | 0.97 → 6.55 (28) |
| Pullback V5 | 2.0× | 188 | 22.3% | 1.39 | +0.285R | -58.75R | 1.05 | 0.95 → 6.51 (28) |
| Pullback V5 | 2.5× | 182 | 26.4% | 1.50 | +0.294R | -37.35R | 1.14 | 1.09 → 6.38 (27) |
| Pullback V5 | 3.0× | 181 | 26.5% | 1.45 | +0.231R | -32.32R | 1.11 | 1.05 → 5.96 (27) |

#### PAXG D1

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Max DD | PF phí 0.1% | PF in-sample → ngoài mẫu (lệnh OOS) |
|---|---|---|---|---|---|---|---|---|
| Breakout | 1.0× | 12 | 33.3% | 10.34 | **+6.720R** | -4.34R | 9.25 | 11.21 → không có lệnh |
| Breakout | 1.5× | 12 | 41.7% | 9.10 | +4.873R | -4.22R | 8.39 | 9.64 → không có lệnh |
| Breakout | 2.0× | 12 | 50.0% | 8.46 | +3.660R | -3.15R | 7.88 | 8.89 → không có lệnh |
| Breakout | 2.5× | 11 | 54.5% | 9.75 | +3.450R | -1.74R | 9.16 | 10.18 → không có lệnh |
| Breakout | 3.0× | 9 | **66.7%** | **14.70** | +3.234R | -1.62R | **13.70** | 15.45 → không có lệnh |
| Breakout | 3.5× | 9 | **66.7%** | 13.63 | +2.756R | -1.53R | 12.76 | 14.28 → không có lệnh |
| Breakout | 4.0× | 9 | **66.7%** | 14.43 | +2.422R | **-1.24R** | 13.46 | 15.15 → không có lệnh |
| Pullback V5 | 1.5× | 9 | 33.3% | 4.75 | +2.386R | -2.59R | 4.39 | 4.11 → ∞ (1) |
| Pullback V5 | 2.0× | 8 | 50.0% | 6.42 | +2.043R | -1.97R | 5.92 | 5.52 → ∞ (1) |
| Pullback V5 | 2.5× | 8 | 50.0% | 5.82 | +1.604R | -1.62R | 5.40 | 4.98 → ∞ (1) |
| Pullback V5 | 3.0× | 8 | 50.0% | 5.42 | +1.315R | -1.35R | 5.04 | 4.61 → ∞ (1) |

**Nhận xét:**
- **H4 là khung tốt nhất cho vàng** (khác BTC, nơi H1 tốt nhất). Breakout lãi đều ở ATR 2.0–4.0× (PF 2.4–2.6, vẫn trên 2.0 khi phí 0.1%) — kết quả không phụ thuộc một mức ATR duy nhất. Lãi phân bố khá đều: ở 2.0×, tổng +45.5R, bỏ 3 lệnh lãi nhất vẫn còn +17.6R (BTC H4 bỏ 3 lệnh lớn nhất là lỗ -19.8R). Theo năm (2.0×): 2021 +0.8R, 2022 +7.9R, 2023 -4.4R, 2024 +19.8R, 2025 +13.1R, 2026 +8.3R — kể cả 2021–2023 khi giá vàng gần như đi ngang cũng không lỗ nặng.
- **Pullback V5 H4 là phương án tương đương Breakout**: ở 2.0–2.5×, PF 2.50–2.79, DD chỉ -3.9 đến -4.1R, R/DD 7.2–7.4 (Breakout 6.4–7.0); bỏ 3 lệnh lớn nhất vẫn còn +7 đến +9.5R. Kiểu "cắt xuống rồi cắt lại" hiếm (9 lệnh) nhưng rất tốt (PF 5–6), kiểu "chạm rồi bật" 31 lệnh PF 2.1–2.4. Đổi lại tổng R thấp hơn Breakout (+28–31R so với +32–41R) và ngoài mẫu chỉ 6 lệnh (PF 2.3–2.5 so với Breakout 6.2 với 8 lệnh).
- **H1 không nên dùng**: in-sample PF chỉ 0.94–1.36 (gần hòa vốn), lãi gần như toàn bộ đến từ đợt tăng giá 2025–2026 (Breakout 4.0×: 2025–2026 +58R trên tổng +59R; 2021–2022 lỗ); với phí 0.1% phần lớn các mức ATR lỗ. Max DD rất sâu ở ATR hẹp (-100R ở 1.0×).
- **D1 số đẹp nhưng không tin được**: Breakout PF 9–15, Pullback V5 PF 4.7–6.4, đều chỉ 8–12 lệnh trong gần 6 năm; 3 lệnh đóng góp 97% lợi nhuận (Breakout 2.5×: lệnh 27/8/2025 +19.2R), không có lệnh Breakout nào ngoài mẫu (Pullback V5 có đúng 1 lệnh, thắng).
- **Buy & Hold vàng**: 1,931.72 → 4,279.73 (x2.22), Max DD -29.2%.

**Lưu ý riêng cho vàng:**
1. **Giai đoạn test vàng tăng rất mạnh** (cuối năm: 2021 $1,835 → 2023 $2,028 → 2024 $2,633 → 2025 $4,337). Chiến lược đi theo xu hướng đương nhiên được lợi; PF ngoài mẫu 5–6 phản ánh đợt tăng này nhiều hơn chất lượng tín hiệu, và ngoài mẫu H4 chỉ có 8 lệnh.
2. **PAXG khác vàng giao ngay**: PAXG giao dịch cả cuối tuần (biến động trung bình mỗi giờ cuối tuần 0.094% so với 0.153% ngày thường) trong khi thị trường vàng thật đóng cửa; kết quả có thể khác nếu chạy trên XAU/USD.
3. Trượt giá chưa tính, và với thanh khoản mỏng của PAXG thì đây là rủi ro lớn hơn so với BTC.

**Kết luận vàng**: **H4 + Breakout + SL 2.0–3.5×ATR** (hoặc **Pullback V5 2.0–2.5×** nếu ưu tiên DD thấp) là cấu hình có bằng chứng tốt nhất trong toàn dự án (lãi phân bố đều hơn và chịu được phí cao hơn BTC H1), nhưng được test trong giai đoạn vàng tăng rất mạnh — cần theo dõi thêm khi vàng đi ngang hoặc giảm. Chạy lại: `python download_binance.py PAXGUSDT 1h ../data/paxg_h1.csv`, `python download_binance.py PAXGUSDT 4h ../data/paxg_h4.csv`, rồi `python asset_test.py ../data/paxg_h1.csv ../data/paxg_h4.csv PAXG`.

## EUR/USD và USD/EUR — áp dụng cùng chiến lược (3/10/2026)

Dữ liệu: cặp **EUR/USDT trên Binance** (`data/eurusdt_h1.csv`, `data/eurusdt_h4.csv`, tải bằng `download_binance.py`, 2021-01-01 → 2026-10-03; 7 chỗ thiếu nến H1 do Binance bảo trì). **USD/EUR** = giá nghịch đảo (`data/usdeur_*.csv`: open=1/open, high=1/low, low=1/high, close=1/close) — vì chiến lược chỉ mua, "mua USD/EUR" tương đương bán EUR/USD. Chạy `python asset_test.py ../data/eurusdt_h1.csv ../data/eurusdt_h4.csv EURUSD` (và USDEUR) → `results/eurusd_summary.csv`, `results/usdeur_summary.csv`; bảng dưới từ `python fx_fee_check.py` → `results/eurusd_fx_fee.csv`.

**Phí:** EUR/USD biến động rất thấp (ATR(14) trung vị chỉ 0.105% giá ở H1, 0.22% ở H4), nên phí crypto 0.04%/chiều ăn mất 0.09–0.28R mỗi lệnh ở H4 và 0.22–0.70R ở H1 — không công bằng với forex thật. Bảng dưới dùng **phí forex sát thực tế 0.005%/chiều** (spread + hoa hồng ECN), kèm PF không phí. Toàn giai đoạn 2021 → 10/2026; ngoài mẫu = lệnh vào từ 1/10/2025 (phí 0.005%).

| Cặp | Khung | Chiến lược | ATR | Lệnh | Win rate | PF không phí | PF phí 0.005% | Kỳ vọng | Tổng R | Max DD | PF ngoài mẫu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EUR/USD | H4 | Breakout | 1.5× | 54 | 20.4% | 1.03 | 0.98 | -0.011R | -0.6R | -15.5R | 0.66 (8 lệnh) |
| EUR/USD | H4 | Breakout | 2.0× | 53 | 22.6% | 0.87 | 0.84 | -0.115R | -6.1R | -13.0R | 0.53 (8 lệnh) |
| EUR/USD | H4 | Breakout | 2.5× | 53 | 24.5% | 0.96 | 0.93 | -0.046R | -2.4R | -10.6R | 0.47 (8 lệnh) |
| EUR/USD | H4 | Breakout | 3.0× | 52 | 26.9% | 0.94 | 0.91 | -0.050R | -2.6R | -10.0R | 0.42 (8 lệnh) |
| EUR/USD | H4 | Breakout | 4.0× | 52 | 26.9% | 0.83 | 0.81 | -0.090R | -4.7R | -8.8R | 0.43 (8 lệnh) |
| EUR/USD | H4 | Pullback V5 | 2.0× | 42 | 11.9% | 0.24 | 0.23 | -0.563R | -23.7R | -23.7R | 0.00 (5 lệnh) |
| EUR/USD | H4 | Pullback V5 | 2.5× | 41 | 14.6% | 0.25 | 0.24 | -0.488R | -20.0R | -20.0R | 0.00 (5 lệnh) |
| EUR/USD | H4 | Pullback V5 | 3.0× | 41 | 14.6% | 0.24 | 0.23 | -0.447R | -18.3R | -18.3R | 0.00 (5 lệnh) |
| EUR/USD | H1 | Breakout | 1.5× | 243 | 14.0% | 0.86 | 0.78 | -0.197R | -47.9R | -66.2R | 1.33 (38 lệnh) |
| EUR/USD | H1 | Breakout | 2.0× | 231 | 18.2% | 0.82 | 0.75 | -0.195R | -45.1R | -55.4R | 1.15 (38 lệnh) |
| EUR/USD | H1 | Breakout | 2.5× | 223 | 22.0% | 0.81 | 0.74 | -0.177R | -39.5R | -46.6R | 1.09 (37 lệnh) |
| EUR/USD | H1 | Breakout | 3.0× | 222 | 23.0% | 0.81 | 0.75 | -0.158R | -35.1R | -43.2R | 0.97 (37 lệnh) |
| EUR/USD | H1 | Breakout | 4.0× | 218 | 24.8% | 0.80 | 0.74 | -0.133R | -29.0R | -33.0R | 0.84 (37 lệnh) |
| EUR/USD | H1 | Pullback V5 | 2.0× | 147 | 25.9% | 0.88 | 0.80 | -0.139R | -20.4R | -20.8R | 0.57 (29 lệnh) |
| EUR/USD | H1 | Pullback V5 | 2.5× | 146 | 26.7% | 0.78 | 0.72 | -0.177R | -25.8R | -25.8R | 0.49 (29 lệnh) |
| EUR/USD | H1 | Pullback V5 | 3.0× | 144 | 27.8% | 0.77 | 0.71 | -0.154R | -22.2R | -22.2R | 0.47 (29 lệnh) |
| USD/EUR | H4 | Breakout | 1.5× | 75 | 18.7% | 0.64 | 0.61 | -0.308R | -23.1R | -28.3R | 0.27 (12 lệnh) |
| USD/EUR | H4 | Breakout | 2.0× | 73 | 23.3% | 0.62 | 0.60 | -0.284R | -20.8R | -28.2R | 0.22 (12 lệnh) |
| USD/EUR | H4 | Breakout | 2.5× | 72 | 25.0% | 0.67 | 0.65 | -0.223R | -16.1R | -21.8R | 1.02 (11 lệnh) |
| USD/EUR | H4 | Breakout | 3.0× | 71 | 25.4% | 0.62 | 0.60 | -0.228R | -16.2R | -20.4R | 0.90 (11 lệnh) |
| USD/EUR | H4 | Breakout | 4.0× | 69 | 29.0% | 0.67 | 0.65 | -0.149R | -10.3R | -12.3R | 0.81 (11 lệnh) |
| USD/EUR | H4 | Pullback V5 | 2.0× | 48 | 22.9% | 0.54 | 0.52 | -0.333R | -16.0R | -18.5R | 0.37 (8 lệnh) |
| USD/EUR | H4 | Pullback V5 | 2.5× | 47 | 27.7% | 0.57 | 0.55 | -0.270R | -12.7R | -15.6R | 0.32 (8 lệnh) |
| USD/EUR | H4 | Pullback V5 | 3.0× | 46 | 28.3% | 0.57 | 0.55 | -0.236R | -10.9R | -13.5R | 0.41 (7 lệnh) |
| USD/EUR | H1 | Breakout | 1.5× | 222 | 17.1% | 0.77 | 0.70 | -0.255R | -56.6R | -91.1R | 0.39 (32 lệnh) |
| USD/EUR | H1 | Breakout | 2.0× | 216 | 19.9% | 0.74 | 0.68 | -0.241R | -52.0R | -83.0R | 0.34 (31 lệnh) |
| USD/EUR | H1 | Breakout | 2.5× | 209 | 23.9% | 0.84 | 0.78 | -0.144R | -30.1R | -59.9R | 0.43 (29 lệnh) |
| USD/EUR | H1 | Breakout | 3.0× | 207 | 24.6% | 0.79 | 0.74 | -0.157R | -32.5R | -55.4R | 0.38 (29 lệnh) |
| USD/EUR | H1 | Breakout | 4.0× | 197 | 28.4% | 0.90 | 0.85 | -0.072R | -14.1R | -37.3R | 0.86 (28 lệnh) |
| USD/EUR | H1 | Pullback V5 | 2.0× | 153 | 22.9% | 0.84 | 0.77 | -0.166R | -25.3R | -36.1R | 0.62 (22 lệnh) |
| USD/EUR | H1 | Pullback V5 | 2.5× | 149 | 24.2% | 0.77 | 0.72 | -0.186R | -27.7R | -39.3R | 0.55 (22 lệnh) |
| USD/EUR | H1 | Pullback V5 | 3.0× | 148 | 25.7% | 0.78 | 0.72 | -0.159R | -23.5R | -33.6R | 0.48 (22 lệnh) |

Buy & Hold EUR/USD: 1.22 → 1.12 (x0.92, Max DD -27%); USD/EUR x1.09 (Max DD -21%). D1 chỉ 4–7 lệnh mỗi cấu hình, không có ý nghĩa thống kê (xem `results/eurusd_summary.csv`).

**Kết luận EUR/USD: chiến lược không có lợi thế, kể cả khi không tính phí.**
- **PF không phí gần như đều dưới 1** (H1 0.74–0.90, H4 0.24–1.03, cả hai chiều); thêm phí forex thực tế thì lỗ ở mọi cấu hình. Pullback V5 H4 EUR/USD tệ nhất (PF 0.23–0.25).
- Ngoài mẫu EUR/USD H1 Breakout 1.5–2.5× có PF 1.09–1.33 (37–38 lệnh), nhưng trong mẫu cùng cấu hình lỗ đều suốt 2021–2025 → nhiều khả năng là may mắn ngắn hạn, không phải lợi thế.
- Lý do: EUR/USD đi ngang/đảo chiều nhiều, ít xu hướng dài và mạnh như BTC hay vàng — chiến lược đi theo xu hướng với win rate thấp sống nhờ vài lệnh rất lớn, mà EUR/USD hiếm khi cho lệnh lớn.
- Lưu ý dữ liệu: EUR/USDT trên Binance giao dịch 24/7, thanh khoản thấp hơn thị trường forex thật (nghỉ cuối tuần); kết quả trên dữ liệu forex thật có thể khác chút, nhưng PF không phí dưới 1 cho thấy vấn đề nằm ở tín hiệu, không phải ở phí.

## So sánh EMA9/45 với EMA10/50 và các cặp lân cận (9/10/2026)

Cùng luật (lọc EMA nhanh > EMA chậm > EMA200, Breakout/Pullback V5, SL = k×ATR(14), làm nóng 200 nến, SL trong nến vào lệnh bằng nến H1), chỉ đổi chu kỳ EMA. `python ema_pair_test.py <h1> <h4> <tên> 9,45 10,50 ...` (dùng nguyên các hàm của `asset_test.py`) → `results/ema_pair_btc_9_10.csv`, `results/ema_pair_btcnb.csv`, `results/ema_pair_paxg.csv`. BTC: dữ liệu Binance tải mới đến 9/10/2026; vàng: `paxg_*.csv` (đến 27/9/2026). Mọi số **đã trừ phí 0.04%/chiều**; ngoài mẫu = lệnh vào từ 1/10/2025.

**BTC — PF Breakout theo cặp EMA và ATR:**

| EMA | H1 1.5× | H1 2.0× | H1 2.5× | H1 3.0× | H1 3.5× | H4 1.5× | H4 2.0× | H4 2.5× | H4 3.0× | H4 3.5× |
|---|---|---|---|---|---|---|---|---|---|---|
| 8/40 | 1.38 | 1.30 | 1.33 | 1.45 | 1.54 | 1.04 | 1.08 | 1.08 | 1.37 | 1.35 |
| **9/45** | **1.67** | **1.60** | **1.77** | **1.74** | **1.64** | 1.14 | 1.44 | 1.42 | 1.36 | 1.31 |
| 10/50 | 1.54 | 1.34 | 1.33 | 1.44 | 1.36 | 1.53 | **2.16** | **2.01** | **2.02** | **1.84** |
| 11/55 | 1.49 | 1.35 | 1.26 | 1.35 | 1.34 | 1.49 | 1.45 | 1.28 | 1.26 | 1.25 |
| 12/60 | 1.57 | 1.50 | 1.42 | 1.44 | 1.41 | 1.71 | 1.56 | 1.35 | 1.27 | 1.20 |

**BTC Breakout 2.5×:**

| EMA | Khung | Lệnh | Win rate | PF | Tổng R | Max DD | R/DD | Ngoài mẫu |
|---|---|---|---|---|---|---|---|---|
| 9/45 | H1 | 212 | 27.8% | 1.77 | +104.7R | -16.2R | 6.45 | PF 0.84 (35 lệnh) |
| 10/50 | H1 | 190 | 25.8% | 1.33 | +41.4R | -23.5R | 1.76 | PF 1.31 (29 lệnh) |
| 9/45 | H4 | 61 | 24.6% | 1.42 | +15.2R | -10.6R | 1.43 | PF 0.11 (9 lệnh) |
| 10/50 | H4 | 49 | 32.7% | 2.01 | +25.2R | -9.5R | 2.66 | PF 2.62 (4 lệnh) |

**Vàng (PAXG) H4:** EMA10/50 tốt hơn 9/45 — Breakout 2.0× PF 3.23 (46 lệnh, +49.4R, DD -5.4R) so với 2.51 (56 lệnh, +41.4R, DD -6.5R); Pullback V5 2.5× PF 3.73 (32 lệnh, DD -2.7R) so với 2.79 (40 lệnh). Ngoài mẫu chỉ 3–5 lệnh.

**Kết luận:**
- **EMA10/50 không tốt hơn một cách nhất quán**: BTC H1 kém đi rõ (PF 2.5× từ 1.77 xuống 1.33, tổng R giảm hơn một nửa), BTC H4 và vàng H4 tốt lên.
- **Kết quả rất nhạy với chu kỳ EMA — dấu hiệu overfitting**: BTC H1 thì 9/45 là đỉnh đơn lẻ (các cặp lân cận chỉ PF 1.26–1.57); BTC H4 thì 10/50 là đỉnh đơn lẻ (8/40, 11/55, 12/60 chỉ 1.04–1.71). Một cấu hình bền thì các cặp lân cận phải cho kết quả gần giống — ở đây không như vậy. Mọi cặp đều có PF > 1 ở BTC H1 (lợi thế "đi theo xu hướng" có thật nhưng nhỏ hơn con số của riêng 9/45), còn PF 1.77 của 9/45 nhiều khả năng một phần nhờ may mắn chọn đúng tham số.
- **Cập nhật ngoài mẫu BTC H1 9/45 Breakout 2.5×**: với dữ liệu đến 9/10/2026, PF ngoài mẫu tụt từ 1.18 chưa phí / 1.05 sau phí (28 lệnh đến 23/9 — khớp số cũ) xuống **0.96 chưa phí / 0.84 sau phí (35 lệnh)**: 7 lệnh từ 27/9 đến 6/10 thua 6 (5 lệnh -1R liên tiếp), thắng 1 (+1.96R). Chưa đủ để kết luận chiến lược hỏng (win rate thấp, chuỗi thua dài là bình thường), nhưng cần theo dõi; mốc dừng xem xét vẫn là PF ngoài mẫu < 1.0 sau khoảng 50 lệnh.
- **Không đổi sang EMA10/50**: không có bằng chứng ổn định, và chọn cặp EMA tốt nhất cho từng khung sau khi đã nhìn kết quả chính là overfitting.

## Bảng thống kê đầy đủ EMA10 cắt EMA50 (chuyển sang từ 9/10/2026)

Cùng luật với EMA9/45 (lọc EMA10 > EMA50 > EMA200, làm nóng 200 nến, Breakout hoặc Pullback V5, SL = k×ATR(14), lệnh chờ tự hủy, thoát breakdown, SL trong nến vào lệnh xử lý bằng nến H1 cho H4/D1). Chạy `cd scripts` rồi `python ema_full_report.py ../data/btc_h1_binance.csv ../data/btc_h4_binance.csv BTC 10 50` (và `paxg_h1_binance.csv`/`paxg_h4_binance.csv` cho vàng) → `results/ema10_50_btc.csv`, `results/ema10_50_paxg.csv`. Dữ liệu Binance 2021-01-01 → 9/10/2026 (BTC và PAXG tải mới, khớp dữ liệu cũ với sai lệch 0–0.01). Kiểm chứng: 27/27 dòng BTC và 27/27 dòng vàng trùng tuyệt đối với lần chạy `ema_pair_test.py` độc lập trước đó.

Cách đọc: **mọi số đã trừ phí 0.04%/chiều** (trừ cột "PF không phí / phí 0.1%"). Kỳ vọng = R trung bình mỗi lệnh. R/DD = Tổng R ÷ |Max DD|. "$1,000 →" = vốn cuối khi rủi ro 1%/lệnh, lãi kép; "DD vốn" = sụt giảm vốn lớn nhất. Ngoài mẫu = lệnh vào từ 1/10/2025. **In đậm** = ATR tối ưu (R/DD cao nhất sau phí) cho từng khung × chiến lược.

### ATR tối ưu — tóm tắt

| Tài sản | Khung | Chiến lược | ATR tối ưu | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | $1,000 → | PF ngoài mẫu | Đánh giá |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC | H1 | Breakout | 1.5× | 200 | 21.0% | 1.54 | +0.453R | +90.6R | -31.4R | 2.89 | $1,980 | 1.43 (31 lệnh) | Dùng được, DD sâu (chuỗi thua 20) |
| BTC | H1 | Pullback V5 | 2.0× | 156 | 21.8% | 1.44 | +0.317R | +49.5R | -20.5R | 2.41 | $1,411 | 0.90 (28 lệnh) | Yếu ngoài mẫu |
| **BTC** | **H4** | **Breakout** | **2.0×** | 50 | 32.0% | **2.16** | +0.675R | +33.8R | -10.1R | **3.35** | $1,354 | 2.62 (4 lệnh) | **Tốt nhất cho BTC với EMA10/50**, nhưng ngoài mẫu mới 4 lệnh |
| BTC | H4 | Pullback V5 | 3.5× | 36 | 30.6% | 1.40 | +0.153R | +5.5R | -6.1R | 0.90 | $1,052 | 0.36 (4 lệnh) | Không dùng |
| BTC | D1 | Breakout | 1.0× | 10 | 30.0% | 3.34 | +1.548R | +15.5R | -3.1R | 5.05 | $1,153 | 0 (1 lệnh) | Quá ít lệnh |
| **Vàng** | **H4** | **Breakout** | **2.0×** | 46 | 43.5% | **3.23** | +1.073R | +49.4R | -5.4R | **9.22** | $1,596 | 69.1 (4/5 thắng) | **Dùng** |
| **Vàng** | **H4** | **Pullback V5** | **3.0×** | 31 | 45.2% | **4.28** | +0.870R | +27.0R | -2.2R | **12.14** | $1,298 | 4.94 (1/3 thắng) | **Dùng** (DD rất thấp, ít lệnh) |
| Vàng | H1 | Breakout | 4.0× | 194 | 32.5% | 1.69 | +0.274R | +53.2R | -19.4R | 2.75 | $1,559 | 4.50 (25 lệnh) | Lãi phần lớn nhờ đợt tăng 2025–2026; PF giảm mạnh khi phí 0.1% (1.69 → 1.31), DD sâu |
| Vàng | D1 | Breakout | 2.5× | 11 | 54.5% | 10.08 | +3.366R | +37.0R | -1.6R | 23.52 | $1,413 | – (0 lệnh) | Quá ít lệnh |

Buy & Hold cùng giai đoạn: BTC x2.84 (Max DD -77.2%), vàng x2.16 (Max DD -29.2%).

**Nhận xét EMA10/50:**
- **BTC: H4 Breakout 2.0× là cấu hình tốt nhất** (PF 2.16, R/DD 3.35, DD vốn -9.7%, 2.0–3.0× đều PF ≥ 2.0 nên không phụ thuộc một mức ATR). Nhưng chỉ 50 lệnh trong ~6 năm và ngoài mẫu mới 4 lệnh; các cặp EMA lân cận (8/40, 11/55, 12/60) chỉ cho PF 1.08–1.56 ở H4 (xem mục "So sánh EMA9/45 với EMA10/50") → con số 2.16 có rủi ro là may mắn tham số.
- **BTC H1 yếu hơn hẳn EMA9/45** (R/DD tốt nhất 2.89 so với 6.45; tổng R 2.5× +41R so với +105R) nhưng **ngoài mẫu lại tốt hơn** (Breakout 1.5–4.0× PF ngoài mẫu 1.14–1.43, trong khi 9/45 2.5× là 0.84). Breakout 1.0–1.5× có chuỗi thua 20–34 lệnh, DD vốn -27% đến -36%.
- **Vàng H4 tốt ở mọi mức ATR 1.5–4.0×** cả Breakout và Pullback V5 (PF 2.2–4.3, vẫn ≥ 1.9 khi phí 0.1%); lưu ý giai đoạn test vàng tăng mạnh (x2.16).
- **Pullback V5 BTC H4 và Breakout/Pullback 1.0× ở H1/H4** không có lợi thế; D1 chỉ 8–12 lệnh, không có ý nghĩa thống kê.
- **Trên TradingView**: mở Settings của strategy → Inputs → **Fast EMA = 10, Slow EMA = 50**, chọn Entry type và "Stop loss = k x ATR(14)" theo bảng (vd BTC H4 Breakout 2.0, vàng H4 Breakout 2.0 hoặc Pullback 3.0). Script tính EMA giống Python nên các mức trên biểu đồ khớp với bảng này.

### Bảng chi tiết theo khung

##### BTC/USDT — H1

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | TB thắng / thua | Chuỗi thua | $1,000 → | DD vốn | PF không phí / phí 0.1% | PF ngoài mẫu (thắng/lệnh) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Breakout | 1.0× | 205 | 13.2% | 1.49 | +0.493R | +101.1R | -42.99R | 2.35 | +11.35 / -1.15R | 34 | $1,802 | -35.5% | 1.75 / 1.21 | 0.67 (6/33) |
| **Breakout** | **1.5×** | 200 | 21.0% | **1.54** | +0.453R | +90.6R | -31.37R | **2.89** | +6.14 / -1.06R | 20 | $1,980 | -27.1% | 1.74 / 1.31 | 1.43 (11/31) |
| Breakout | 2.0× | 196 | 23.0% | 1.34 | +0.262R | +51.4R | -26.54R | 1.94 | +4.50 / -1.00R | 20 | $1,461 | -23.4% | 1.48 / 1.17 | 1.14 (11/31) |
| Breakout | 2.5× | 190 | 25.8% | 1.33 | +0.218R | +41.4R | -23.50R | 1.76 | +3.42 / -0.89R | 20 | $1,382 | -21.0% | 1.45 / 1.17 | 1.31 (13/29) |
| Breakout | 3.0× | 187 | 28.3% | 1.44 | +0.254R | +47.5R | -21.70R | 2.19 | +2.94 / -0.81R | 20 | $1,501 | -19.6% | 1.56 / 1.28 | 1.34 (14/29) |
| Breakout | 3.5× | 186 | 28.5% | 1.36 | +0.190R | +35.4R | -20.62R | 1.72 | +2.52 / -0.74R | 20 | $1,352 | -18.7% | 1.47 / 1.22 | 1.40 (14/28) |
| Breakout | 4.0× | 186 | 28.5% | 1.29 | +0.140R | +26.0R | -19.82R | 1.31 | +2.20 / -0.68R | 20 | $1,245 | -18.1% | 1.39 / 1.15 | 1.28 (14/28) |
| Pullback V5 | 1.0× | 159 | 13.2% | 0.69 | -0.304R | -48.4R | -61.71R | -0.78 | +5.17 / -1.14R | 17 | $582 | -48.7% | 0.82 / 0.55 | 0.80 (6/29) |
| Pullback V5 | 1.5× | 159 | 16.4% | 0.81 | -0.166R | -26.4R | -35.87R | -0.73 | +4.22 / -1.02R | 17 | $724 | -33.9% | 0.92 / 0.68 | 0.74 (8/29) |
| **Pullback V5** | **2.0×** | 156 | 21.8% | **1.44** | +0.317R | +49.5R | -20.49R | **2.41** | +4.79 / -0.93R | 15 | $1,411 | -19.6% | 1.59 / 1.25 | 0.90 (10/28) |
| Pullback V5 | 2.5× | 154 | 22.7% | 1.40 | +0.248R | +38.2R | -19.58R | 1.95 | +3.85 / -0.81R | 15 | $1,324 | -18.5% | 1.53 / 1.23 | 0.89 (10/28) |
| Pullback V5 | 3.0× | 152 | 23.0% | 1.32 | +0.181R | +27.5R | -20.43R | 1.35 | +3.20 / -0.72R | 15 | $1,223 | -19.0% | 1.45 / 1.17 | 0.82 (10/28) |
| Pullback V5 | 3.5× | 151 | 23.2% | 1.28 | +0.141R | +21.3R | -17.46R | 1.22 | +2.78 / -0.65R | 15 | $1,171 | -16.5% | 1.39 / 1.14 | 0.74 (10/28) |
| Pullback V5 | 4.0× | 149 | 23.5% | 1.27 | +0.120R | +18.0R | -15.29R | 1.17 | +2.43 / -0.59R | 15 | $1,146 | -14.5% | 1.38 / 1.13 | 0.69 (10/28) |

##### BTC/USDT — H4

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | TB thắng / thua | Chuỗi thua | $1,000 → | DD vốn | PF không phí / phí 0.1% | PF ngoài mẫu (thắng/lệnh) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Breakout | 1.0× | 55 | 18.2% | 0.76 | -0.202R | -11.1R | -22.72R | -0.49 | +3.58 / -1.04R | 10 | $880 | -21.1% | 0.83 / 0.68 | 0.69 (3/5) |
| Breakout | 1.5× | 52 | 26.9% | 1.53 | +0.382R | +19.9R | -10.82R | 1.84 | +4.12 / -0.99R | 10 | $1,180 | -10.3% | 1.61 / 1.42 | 0.48 (3/5) |
| **Breakout** | **2.0×** | 50 | 32.0% | **2.16** | +0.675R | +33.8R | -10.08R | **3.35** | +3.93 / -0.86R | 7 | $1,354 | -9.7% | 2.25 / 2.02 | 2.62 (3/4) |
| Breakout | 2.5× | 49 | 32.7% | 2.01 | +0.514R | +25.2R | -9.46R | 2.66 | +3.14 / -0.76R | 7 | $1,257 | -9.1% | 2.08 / 1.89 | 2.62 (3/4) |
| Breakout | 3.0× | 47 | 36.2% | 2.02 | +0.457R | +21.5R | -7.27R | 2.95 | +2.50 / -0.70R | 5 | $1,220 | -7.1% | 2.10 / 1.92 | 2.62 (3/4) |
| Breakout | 3.5× | 47 | 36.2% | 1.84 | +0.353R | +16.6R | -7.23R | 2.30 | +2.14 / -0.66R | 5 | $1,166 | -7.0% | 1.90 / 1.75 | 2.62 (3/4) |
| Breakout | 4.0× | 47 | 36.2% | 1.70 | +0.279R | +13.1R | -7.20R | 1.82 | +1.87 / -0.62R | 5 | $1,129 | -7.0% | 1.75 / 1.62 | 2.62 (3/4) |
| Pullback V5 | 1.0× | 42 | 14.3% | 0.95 | -0.048R | -2.0R | -23.75R | -0.09 | +5.80 / -1.02R | 19 | $950 | -21.2% | 1.02 / 0.85 | 0.57 (2/4) |
| Pullback V5 | 1.5× | 40 | 17.5% | 1.00 | -0.002R | -0.1R | -21.22R | -0.00 | +4.34 / -0.92R | 19 | $982 | -19.2% | 1.05 / 0.92 | 0.39 (2/4) |
| Pullback V5 | 2.0× | 39 | 20.5% | 0.91 | -0.059R | -2.3R | -16.38R | -0.14 | +3.03 / -0.86R | 13 | $967 | -15.2% | 0.96 / 0.85 | 0.33 (2/4) |
| Pullback V5 | 2.5× | 39 | 23.1% | 0.88 | -0.071R | -2.8R | -12.95R | -0.21 | +2.23 / -0.76R | 9 | $966 | -12.2% | 0.92 / 0.82 | 0.36 (2/4) |
| Pullback V5 | 3.0× | 36 | 30.6% | 1.37 | +0.168R | +6.0R | -6.93R | 0.87 | +2.04 / -0.66R | 4 | $1,056 | -6.7% | 1.43 / 1.29 | 0.36 (2/4) |
| **Pullback V5** | **3.5×** | 36 | 30.6% | **1.40** | +0.153R | +5.5R | -6.13R | **0.90** | +1.75 / -0.55R | 4 | $1,052 | -6.0% | 1.46 / 1.32 | 0.36 (2/4) |
| Pullback V5 | 4.0× | 36 | 30.6% | 1.38 | +0.128R | +4.6R | -5.74R | 0.80 | +1.53 / -0.49R | 4 | $1,043 | -5.6% | 1.44 / 1.29 | 0.36 (2/4) |

##### BTC/USDT — D1

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | TB thắng / thua | Chuỗi thua | $1,000 → | DD vốn | PF không phí / phí 0.1% | PF ngoài mẫu (thắng/lệnh) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Breakout** | **1.0×** | 10 | 30.0% | **3.34** | +1.548R | +15.5R | -3.06R | **5.05** | +7.36 / -0.94R | 3 | $1,153 | -3.0% | 3.45 / 3.19 | 0.00 (0/1) |
| Breakout | 1.5× | 10 | 30.0% | 2.38 | +0.854R | +8.5R | -2.82R | 3.02 | +4.91 / -0.88R | 3 | $1,083 | -2.8% | 2.44 / 2.30 | 0.00 (0/1) |
| Breakout | 2.0× | 10 | 30.0% | 1.92 | +0.529R | +5.3R | -2.62R | 2.02 | +3.68 / -0.82R | 3 | $1,051 | -2.6% | 1.96 / 1.87 | 0.00 (0/1) |
| Breakout | 2.5× | 10 | 40.0% | 3.25 | +0.988R | +9.9R | -2.03R | 4.87 | +3.57 / -0.73R | 2 | $1,100 | -2.0% | 3.31 / 3.17 | 0.00 (0/1) |
| Breakout | 3.0× | 10 | 40.0% | 2.86 | +0.774R | +7.7R | -2.03R | 3.82 | +2.98 / -0.69R | 2 | $1,078 | -2.0% | 2.90 / 2.79 | 0.00 (0/1) |
| Breakout | 3.5× | 10 | 40.0% | 2.55 | +0.620R | +6.2R | -2.02R | 3.07 | +2.55 / -0.67R | 2 | $1,062 | -2.0% | 2.59 / 2.50 | 0.00 (0/1) |
| Breakout | 4.0× | 10 | 40.0% | 2.37 | +0.515R | +5.2R | -1.92R | 2.68 | +2.23 / -0.63R | 2 | $1,051 | -1.9% | 2.40 / 2.32 | 0.00 (0/1) |
| Pullback V5 | 1.0× | 8 | 12.5% | 1.84 | +0.754R | +6.0R | -4.10R | 1.47 | +13.22 / -1.03R | 4 | $1,053 | -4.0% | 1.89 / 1.77 | – |
| Pullback V5 | 1.5× | 8 | 12.5% | 1.24 | +0.211R | +1.7R | -4.07R | 0.42 | +8.81 / -1.02R | 4 | $1,013 | -4.0% | 1.26 / 1.20 | – |
| **Pullback V5** | **2.0×** | 8 | 25.0% | **2.60** | +1.173R | +9.4R | -2.81R | **3.34** | +7.62 / -0.97R | 3 | $1,092 | -2.8% | 2.65 / 2.55 | – |
| Pullback V5 | 2.5× | 8 | 25.0% | 2.21 | +0.834R | +6.7R | -2.48R | 2.69 | +6.09 / -0.92R | 3 | $1,065 | -2.5% | 2.24 / 2.17 | – |
| Pullback V5 | 3.0× | 8 | 37.5% | 2.56 | +0.803R | +6.4R | -2.24R | 2.87 | +3.51 / -0.82R | 3 | $1,063 | -2.2% | 2.60 / 2.52 | – |
| Pullback V5 | 3.5× | 8 | 37.5% | 2.54 | +0.683R | +5.5R | -1.81R | 3.01 | +3.01 / -0.71R | 3 | $1,054 | -1.8% | 2.57 / 2.49 | – |
| Pullback V5 | 4.0× | 8 | 37.5% | 2.44 | +0.582R | +4.7R | -1.65R | 2.82 | +2.63 / -0.65R | 3 | $1,046 | -1.6% | 2.47 / 2.39 | – |

##### Vàng PAXG/USDT — H1

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | TB thắng / thua | Chuỗi thua | $1,000 → | DD vốn | PF không phí / phí 0.1% | PF ngoài mẫu (thắng/lệnh) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Breakout | 1.0× | 218 | 17.9% | 0.85 | -0.162R | -35.3R | -98.65R | -0.36 | +5.14 / -1.32R | 35 | $632 | -63.2% | 1.20 / 0.56 | 0.93 (6/28) |
| Breakout | 1.5× | 208 | 22.6% | 1.64 | +0.575R | +119.7R | -66.78R | 1.79 | +6.50 / -1.16R | 17 | $2,069 | -49.6% | 2.10 / 1.22 | 5.96 (7/25) |
| Breakout | 2.0× | 203 | 27.1% | 1.57 | +0.430R | +87.4R | -50.97R | 1.72 | +4.36 / -1.03R | 14 | $1,788 | -40.6% | 1.95 / 1.20 | 5.20 (8/25) |
| Breakout | 2.5× | 197 | 29.9% | 1.63 | +0.389R | +76.7R | -40.91R | 1.88 | +3.37 / -0.89R | 14 | $1,762 | -34.1% | 1.99 / 1.25 | 5.00 (9/25) |
| Breakout | 3.0× | 196 | 30.1% | 1.57 | +0.308R | +60.4R | -35.19R | 1.72 | +2.81 / -0.77R | 14 | $1,581 | -30.1% | 1.91 / 1.22 | 4.79 (9/25) |
| Breakout | 3.5× | 196 | 31.1% | 1.62 | +0.285R | +55.8R | -24.55R | 2.27 | +2.39 / -0.67R | 14 | $1,563 | -22.1% | 1.96 / 1.26 | 4.75 (9/25) |
| **Breakout** | **4.0×** | 194 | 32.5% | **1.69** | +0.274R | +53.2R | -19.36R | **2.75** | +2.06 / -0.58R | 13 | $1,559 | -17.9% | 2.05 / 1.31 | 4.50 (9/25) |
| Pullback V5 | 1.0× | 184 | 10.9% | 0.91 | -0.109R | -20.1R | -161.63R | -0.12 | +9.65 / -1.30R | 38 | $659 | -80.5% | 1.24 / 0.63 | 4.47 (5/21) |
| Pullback V5 | 1.5× | 168 | 20.2% | 1.21 | +0.183R | +30.8R | -57.62R | 0.53 | +5.31 / -1.12R | 31 | $1,237 | -44.8% | 1.55 / 0.88 | 2.94 (6/20) |
| Pullback V5 | 2.0× | 165 | 23.6% | 1.19 | +0.138R | +22.8R | -41.01R | 0.56 | +3.62 / -0.94R | 20 | $1,187 | -34.4% | 1.50 / 0.89 | 2.65 (6/19) |
| Pullback V5 | 2.5× | 161 | 26.1% | 1.20 | +0.117R | +18.9R | -32.44R | 0.58 | +2.74 / -0.81R | 19 | $1,164 | -28.2% | 1.49 / 0.90 | 2.50 (6/19) |
| Pullback V5 | 3.0× | 160 | 26.2% | 1.17 | +0.087R | +14.0R | -25.56R | 0.55 | +2.31 / -0.70R | 19 | $1,119 | -22.9% | 1.44 / 0.89 | 2.21 (6/19) |
| **Pullback V5** | **3.5×** | 160 | 28.1% | **1.27** | +0.114R | +18.2R | -17.85R | **1.02** | +1.91 / -0.59R | 19 | $1,176 | -16.7% | 1.57 / 0.96 | 2.33 (6/19) |
| Pullback V5 | 4.0× | 160 | 28.1% | 1.25 | +0.093R | +14.9R | -15.52R | 0.96 | +1.67 / -0.53R | 19 | $1,143 | -14.6% | 1.54 / 0.94 | 2.22 (6/19) |

##### Vàng PAXG/USDT — H4

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | TB thắng / thua | Chuỗi thua | $1,000 → | DD vốn | PF không phí / phí 0.1% | PF ngoài mẫu (thắng/lệnh) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Breakout | 1.0× | 52 | 23.1% | 1.45 | +0.398R | +20.7R | -27.71R | 0.75 | +5.55 / -1.15R | 8 | $1,181 | -24.4% | 1.71 / 1.17 | 4.99 (3/5) |
| Breakout | 1.5× | 47 | 38.3% | 2.44 | +0.877R | +41.2R | -10.58R | 3.90 | +3.88 / -0.99R | 7 | $1,463 | -10.2% | 2.79 / 2.04 | 3.44 (3/5) |
| **Breakout** | **2.0×** | 46 | 43.5% | **3.23** | +1.073R | +49.4R | -5.36R | **9.22** | +3.58 / -0.85R | 7 | $1,596 | -5.2% | 3.60 / 2.77 | 69.14 (4/5) |
| Breakout | 2.5× | 45 | 44.4% | 3.06 | +0.838R | +37.7R | -4.65R | 8.12 | +2.80 / -0.73R | 7 | $1,434 | -4.6% | 3.39 / 2.64 | 69.14 (4/5) |
| Breakout | 3.0× | 45 | 44.4% | 2.91 | +0.681R | +30.7R | -3.94R | 7.77 | +2.34 / -0.64R | 7 | $1,343 | -3.9% | 3.21 / 2.52 | 69.14 (4/5) |
| Breakout | 3.5× | 44 | 45.5% | 2.92 | +0.598R | +26.3R | -3.52R | 7.47 | +2.00 / -0.57R | 7 | $1,290 | -3.5% | 3.22 / 2.54 | 69.14 (4/5) |
| Breakout | 4.0× | 44 | 45.5% | 2.82 | +0.514R | +22.6R | -3.21R | 7.05 | +1.75 / -0.52R | 7 | $1,245 | -3.2% | 3.10 / 2.46 | 69.14 (4/5) |
| Pullback V5 | 1.0× | 35 | 25.7% | 2.77 | +1.426R | +49.9R | -10.21R | 4.89 | +8.68 / -1.08R | 5 | $1,554 | -9.9% | 3.24 / 2.26 | 7.43 (1/3) |
| Pullback V5 | 1.5× | 35 | 28.6% | 2.24 | +0.849R | +29.7R | -10.01R | 2.97 | +5.36 / -0.96R | 5 | $1,309 | -9.6% | 2.53 / 1.90 | 5.13 (1/3) |
| Pullback V5 | 2.0× | 33 | 36.4% | 2.86 | +0.929R | +30.7R | -3.18R | 9.65 | +3.93 / -0.78R | 3 | $1,334 | -3.1% | 3.19 / 2.46 | 4.31 (1/3) |
| Pullback V5 | 2.5× | 32 | 43.8% | 3.73 | +0.933R | +29.9R | -2.70R | 11.04 | +2.91 / -0.61R | 3 | $1,332 | -2.7% | 4.19 / 3.18 | 4.94 (1/3) |
| **Pullback V5** | **3.0×** | 31 | 45.2% | **4.28** | +0.870R | +27.0R | -2.22R | **12.14** | +2.51 / -0.48R | 3 | $1,298 | -2.2% | 4.81 / 3.63 | 4.94 (1/3) |
| Pullback V5 | 3.5× | 31 | 45.2% | 4.18 | +0.741R | +23.0R | -1.91R | 12.00 | +2.15 / -0.42R | 3 | $1,250 | -1.9% | 4.70 / 3.56 | 4.94 (1/3) |
| Pullback V5 | 4.0× | 31 | 45.2% | 4.10 | +0.644R | +20.0R | -1.67R | 11.93 | +1.89 / -0.38R | 3 | $1,215 | -1.7% | 4.60 / 3.50 | 4.94 (1/3) |

##### Vàng PAXG/USDT — D1

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | TB thắng / thua | Chuỗi thua | $1,000 → | DD vốn | PF không phí / phí 0.1% | PF ngoài mẫu (thắng/lệnh) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Breakout | 1.0× | 12 | 33.3% | 10.21 | +6.627R | +79.5R | -4.34R | 18.33 | +22.04 / -1.08R | 4 | $1,956 | -4.3% | 11.06 / 9.13 | – |
| Breakout | 1.5× | 12 | 41.7% | 9.25 | +4.738R | +56.9R | -3.90R | 14.58 | +12.75 / -0.98R | 4 | $1,662 | -3.8% | 9.82 / 8.50 | – |
| Breakout | 2.0× | 12 | 50.0% | 8.95 | +3.574R | +42.9R | -2.65R | 16.17 | +8.05 / -0.90R | 3 | $1,482 | -2.6% | 9.44 / 8.29 | – |
| **Breakout** | **2.5×** | 11 | 54.5% | **10.08** | +3.366R | +37.0R | -1.57R | **23.52** | +6.85 / -0.81R | 2 | $1,413 | -1.6% | 10.56 / 9.44 | – |
| Breakout | 3.0× | 9 | 66.7% | 16.94 | +3.193R | +28.7R | -1.40R | 20.52 | +5.09 / -0.60R | 2 | $1,313 | -1.4% | 17.95 / 15.60 | – |
| Breakout | 3.5× | 9 | 66.7% | 15.51 | +2.721R | +24.5R | -1.34R | 18.24 | +4.36 / -0.56R | 2 | $1,263 | -1.3% | 16.36 / 14.37 | – |
| Breakout | 4.0× | 9 | 66.7% | 16.58 | +2.392R | +21.5R | -1.08R | 19.93 | +3.82 / -0.46R | 2 | $1,230 | -1.1% | 17.55 / 15.29 | – |
| Pullback V5 | 1.0× | 10 | 20.0% | 3.77 | +2.362R | +23.6R | -3.21R | 7.35 | +16.07 / -1.07R | 3 | $1,230 | -3.2% | 4.04 / 3.42 | 0.00 (0/1) |
| Pullback V5 | 1.5× | 10 | 30.0% | 3.88 | +1.954R | +19.5R | -2.84R | 6.87 | +8.78 / -0.97R | 3 | $1,198 | -2.8% | 4.10 / 3.59 | ∞ (1/1) |
| Pullback V5 | 2.0× | 9 | 44.4% | 4.88 | +1.676R | +15.1R | -2.24R | 6.73 | +4.74 / -0.78R | 3 | $1,156 | -2.2% | 5.16 / 4.50 | ∞ (1/1) |
| Pullback V5 | 2.5× | 9 | 44.4% | 4.86 | +1.340R | +12.1R | -1.60R | 7.53 | +3.80 / -0.62R | 3 | $1,124 | -1.6% | 5.14 / 4.49 | ∞ (1/1) |
| Pullback V5 | 3.0× | 8 | 50.0% | 6.95 | +1.354R | +10.8R | -1.33R | 8.11 | +3.16 / -0.46R | 3 | $1,112 | -1.3% | 7.38 / 6.38 | ∞ (1/1) |
| **Pullback V5** | **3.5×** | 8 | 50.0% | **6.95** | +1.160R | +9.3R | -1.14R | **8.11** | +2.71 / -0.39R | 3 | $1,095 | -1.1% | 7.38 / 6.38 | ∞ (1/1) |
| Pullback V5 | 4.0× | 8 | 50.0% | 6.95 | +1.015R | +8.1R | -1.00R | 8.11 | +2.37 / -0.34R | 3 | $1,083 | -1.0% | 7.38 / 6.38 | ∞ (1/1) |

## Khung 15m — BTC/USDT (13/10/2026)

Dữ liệu `data/btc_m15_binance.csv` (Binance, 2021-01-01 → 13/10/2026, 202,647 nến; 7 chỗ thiếu nến trùng các lần Binance bảo trì như H1). Chạy `cd scripts` rồi `python ema_tf_report.py ../data/btc_m15_binance.csv BTC 15m 6.0 9 45` (và `... 10 50`) → `results/ema9_45_btc_15m.csv`, `results/ema10_50_btc_15m.csv`. Script `ema_tf_report.py` dùng nguyên các hàm của `asset_test.py`; kiểm chứng bằng cách chạy nó trên H1 → trùng tuyệt đối 14/14 dòng với `results/ema10_50_btc.csv`. Không có nến nhỏ hơn 15m nên SL trong nến vào lệnh dùng giả định bất lợi như H1 (lưu ý #9). Đã trừ phí 0.04%/chiều (cột "phí/lệnh" = phí quy ra R trung bình); ngoài mẫu = lệnh vào từ 1/10/2025.

### EMA9/45 — 15m

| Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Tổng R | Max DD | R/DD | Chuỗi thua | $1,000 → | DD vốn | Phí/lệnh | PF không phí / phí 0.1% | PF ngoài mẫu (thắng/lệnh) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Breakout | 1.0× | 1110 | 12.9% | 0.97 | -0.035R | -38.5R | -185.9R | -0.21 | 37 | $176 | -86.7% | 0.35R | 1.36 / 0.66 | 0.69 (18/175) |
| Breakout | 1.5× | 1088 | 17.9% | 1.22 | +0.210R | +228.5R | -122.1R | 1.87 | 21 | $2,323 | -74.0% | 0.23R | 1.57 / 0.89 | 1.84 (29/173) |
| Breakout | 2.0× | 1052 | 21.9% | 1.26 | +0.216R | +227.6R | -85.7R | 2.66 | 21 | $3,757 | -60.7% | 0.17R | 1.56 / 0.96 | 1.70 (34/169) |
| **Breakout** | **2.5×** | 1015 | 24.7% | **1.28** | +0.204R | +206.6R | -51.9R | **3.98** | 20 | $4,085 | -43.4% | 0.14R | 1.56 / 0.99 | 1.61 (39/162) |
| Breakout | 3.0× | 989 | 25.9% | 1.29 | +0.180R | +178.3R | -47.3R | 3.77 | 20 | $3,671 | -38.4% | 0.12R | 1.55 / 1.01 | 1.56 (39/158) |
| Breakout | 3.5× | 982 | 26.5% | 1.27 | +0.148R | +145.3R | -41.1R | 3.54 | 20 | $2,966 | -35.9% | 0.10R | 1.52 / 1.00 | 1.59 (40/155) |
| Breakout | 4.0× | 969 | 27.3% | 1.29 | +0.140R | +135.4R | -36.5R | 3.71 | 19 | $2,903 | -32.4% | 0.09R | 1.54 / 1.01 | 1.58 (41/153) |
| Pullback V5 | 1.0× | 830 | 14.2% | 1.02 | +0.025R | +20.7R | -111.8R | 0.18 | 37 | $500 | -74.5% | 0.34R | 1.44 / 0.69 | 0.63 (20/132) |
| **Pullback V5** | **1.5×** | 809 | 19.5% | **1.10** | +0.089R | +72.3R | -58.1R | **1.24** | 19 | $1,237 | -45.7% | 0.23R | 1.43 / 0.79 | 0.71 (26/131) |
| Pullback V5 | 2.0× | 789 | 21.5% | 1.08 | +0.065R | +51.4R | -55.4R | 0.93 | 19 | $1,157 | -45.9% | 0.17R | 1.37 / 0.81 | 0.65 (28/128) |
| Pullback V5 | 2.5× | 768 | 23.6% | 1.07 | +0.050R | +38.5R | -45.6R | 0.84 | 19 | $1,152 | -37.2% | 0.14R | 1.33 / 0.82 | 0.66 (33/121) |
| Pullback V5 | 3.0× | 760 | 24.7% | 1.07 | +0.042R | +32.2R | -40.6R | 0.79 | 17 | $1,158 | -33.9% | 0.11R | 1.32 / 0.82 | 0.65 (35/121) |
| Pullback V5 | 3.5× | 750 | 25.3% | 1.08 | +0.039R | +29.1R | -34.4R | 0.84 | 17 | $1,173 | -29.5% | 0.10R | 1.32 / 0.83 | 0.65 (35/119) |
| Pullback V5 | 4.0× | 747 | 25.4% | 1.07 | +0.033R | +24.6R | -31.1R | 0.79 | 17 | $1,154 | -27.0% | 0.09R | 1.31 / 0.83 | 0.64 (35/118) |

EMA10/50 — 15m (tóm tắt, chi tiết trong `results/ema10_50_btc_15m.csv`): Breakout tối ưu 4.0× (869 lệnh, PF 1.37, +162.2R, Max DD -39.3R, R/DD 4.12, ngoài mẫu PF 1.91 / 134 lệnh); 2.5× PF 1.32, +212.4R, Max DD -60.5R. Pullback V5 không có lợi thế (PF 0.95–1.16, ngoài mẫu 0.80–0.88).

**Kiểm tra độ tin cậy (EMA9/45 Breakout 2.5×):**
- **Phụ thuộc vài lệnh lớn**: bỏ 1 lệnh lớn nhất → +112.1R (PF 1.15); bỏ 5 → +19.4R (PF 1.03); bỏ 10 → -53.6R (PF 0.93). Lệnh lớn nhất (vào 19/8/2026, +94.5R) có **SL chỉ 0.20% giá** và giá tăng 19.2% → R bị phóng đại vì SL hẹp; vào lệnh rủi ro 1% cần đòn bẩy ~5x. **Ngoài mẫu (+77.5R) bỏ riêng lệnh này thì còn -17.0R** → PF ngoài mẫu 1.61 gần như nhờ một lệnh.
- **Theo năm**: 2021 -1.2R (PF 0.99), 2022 -31.7R (0.73), 2023 +83.2R (1.61), 2024 +83.1R (1.66), 2025 -9.2R (0.92), 2026 +82.4R (1.82).
- **Rất nhạy với phí và trượt giá**: SL trung vị chỉ 0.72% giá (5% số lệnh dưới 0.24%, 95 lệnh dưới 0.3%), phí 0.04%/chiều ăn trung bình 0.14R/lệnh, có lệnh tới 1R. Phí 0.1%/chiều → PF 0.99 (hòa vốn). Trượt giá chưa tính — với SL 0.2–0.3% giá, trượt 0.05% đã mất 0.2R mỗi lần.
- **Max DD lớn là đúng, không phải lỗi** (đã kiểm chứng): tính lại bằng vòng lặp độc lập ra đúng số; trước phí không có lệnh nào lỗ quá -1R (khớp SL đúng); Max DD -51.9R của EMA9/45 2.5× kéo dài từ 26/10/2025 đến 18/8/2026 (~125 lệnh) và chỉ được gỡ lại nhờ lệnh +94.5R ngày 19/8. Với EMA10/50 2.5×, Max DD -60.5R kéo dài 13/3/2021 → 8/1/2023 (287 lệnh, BTC 60,637 → 16,954, thắng 22%): trước phí -29.9R, **phí -30.6R** — một nửa DD là phí. Quy ra vốn: -60R ≈ -48.5% vốn khi rủi ro 1%/lệnh, -27.2% khi rủi ro 0.5%/lệnh.

**Kết luận 15m:** tổng R và vốn cuối cao hơn H1 chủ yếu vì số lệnh gấp ~5 lần và một lệnh +94.5R, **không phải vì mỗi lệnh tốt hơn** — so với H1 EMA9/45 Breakout 2.5× (PF 1.77, Max DD -16.2R, R/DD 6.45, dữ liệu đến 9/10/2026) thì 15m kém hơn ở PF, Max DD và độ bền khi phí cao. Strategy Tester trên TradingView gói miễn phí chỉ tải khoảng 1–2 tháng nến 15m, trùng giai đoạn 15m đang thắng (2026 PF 1.82) nên trông tốt hơn thực tế. Nếu vẫn dùng 15m: Breakout ATR 2.5–3.0×, rủi ro ≤ 0.5%/lệnh, phí thấp (futures maker hoặc giảm phí), và cân nhắc bỏ qua tín hiệu có SL quá hẹp.

## Pullback V5: bộ lọc "EMA9 > EMA45 > EMA200" (A) so với "EMA9 cắt EMA45 và giá > EMA200" (B) (17/10/2026)

Bộ lọc B: tín hiệu Pullback chỉ cần EMA9 cắt lên EMA45 với **giá đóng cửa > EMA200** (không cần EMA45 > EMA200); điều kiện này áp cho nến cắt lên, nến tín hiệu Pullback và nến trước nến vào lệnh (đúng chỗ bộ lọc A đang áp). Mọi luật khác giữ nguyên. Chạy `cd scripts` rồi `python ema_full_report.py ../data/btc_h1_binance.csv ../data/btc_h4_binance.csv BTC 9 45 A` (và `... B`; tương tự cho `paxg_*_binance.csv`) → `results/ema9_45_{btc,paxg}.csv` (A), `results/ema9_45_locB_{btc,paxg}.csv` (B). Kiểm chứng định nghĩa bộ lọc B: chạy Breakout + B trên đúng dữ liệu cũ tái tạo chính xác số đã ghi ở mục "Kết luận tổng hợp" phần 4 (BTC H4 2.0×: PF 1.70 / +35.3R / -13.6R; vàng H4 2.5×: PF 2.71 / +56.3R / -5.6R). Dữ liệu Binance đến 17/10/2026; đã trừ phí 0.04%/chiều; ngoài mẫu = lệnh vào từ 1/10/2025. **In đậm** = ATR tối ưu (R/DD cao nhất) của từng bộ lọc.

##### BTC/USDT — H1 (Pullback V5)

| ATR | Lệnh A / B | Win rate A / B | PF A / B | Kỳ vọng A / B | Tổng R A / B | Max DD A / B | R/DD A / B | Ngoài mẫu A | Ngoài mẫu B |
|---|---|---|---|---|---|---|---|---|---|
| 1.0× | 173 / 235 | 12.7% / 14.5% | 1.05 / 1.19 | +0.053 / +0.179R | +9.1 / +42.1R | -45.2 / -43.7R | 0.20 / 0.96 | PF 0.43, -18.7R (32 lệnh) | PF 0.46, -24.2R (45 lệnh) |
| 1.5× | 170 / 232 | 18.8% / 19.8% | 1.09 / 1.13 | +0.075 / +0.112R | +12.7 / +25.9R | -30.3 / -36.5R | 0.42 / 0.71 | PF 0.53, -12.0R (30 lệnh) | PF 0.49, -18.4R (43 lệnh) |
| 2.0× | 169 / 228 | 23.1% / 25.0% | 1.65 / 1.64 | +0.478 / +0.462R | +80.8 / +105.4R | -24.3 / -21.5R | 3.32 / 4.91 | PF 0.51, -11.4R (30 lệnh) | PF 0.46, -17.9R (43 lệnh) |
| 2.5× | 163 / 220 | 26.4% / 28.2% | **1.81** / **1.78** | +0.487 / +0.468R | +79.4 / +103.1R | -13.1 / -13.1R | **6.06** / **7.90** | PF 0.95, -0.7R (27 lệnh) | PF 0.70, -7.2R (40 lệnh) |
| 3.0× | 162 / 219 | 27.2% / 28.8% | 1.70 / 1.68 | +0.376 / +0.363R | +61.0 / +79.6R | -13.4 / -12.2R | 4.54 / 6.55 | PF 0.84, -2.3R (27 lệnh) | PF 0.64, -7.9R (40 lệnh) |
| 3.5× | 160 / 217 | 27.5% / 29.0% | 1.69 / 1.66 | +0.328 / +0.312R | +52.4 / +67.6R | -11.3 / -11.4R | 4.63 / 5.92 | PF 0.77, -3.1R (27 lệnh) | PF 0.59, -8.2R (40 lệnh) |
| 4.0× | 159 / 216 | 27.7% / 29.2% | 1.67 / 1.63 | +0.283 / +0.265R | +45.0 / +57.3R | -11.1 / -11.1R | 4.04 / 5.15 | PF 0.70, -3.8R (27 lệnh) | PF 0.56, -8.3R (40 lệnh) |

##### BTC/USDT — H4 (Pullback V5)

| ATR | Lệnh A / B | Win rate A / B | PF A / B | Kỳ vọng A / B | Tổng R A / B | Max DD A / B | R/DD A / B | Ngoài mẫu A | Ngoài mẫu B |
|---|---|---|---|---|---|---|---|---|---|
| 1.0× | 42 / 52 | 11.9% / 11.5% | 0.53 / 0.49 | -0.443 / -0.470R | -18.6 / -24.4R | -18.6 / -24.4R | -1.00 / -1.00 | PF 0.33, -1.4R (3 lệnh) | PF 0.13, -4.7R (6 lệnh) |
| 1.5× | 42 / 52 | 16.7% / 15.4% | 0.63 / 0.56 | -0.289 / -0.351R | -12.1 / -18.2R | -16.5 / -18.4R | -0.73 / -0.99 | PF 0.33, -0.9R (3 lệnh) | PF 0.10, -4.1R (6 lệnh) |
| 2.0× | 42 / 52 | 16.7% / 15.4% | 0.52 / 0.45 | -0.348 / -0.397R | -14.6 / -20.6R | -15.1 / -20.6R | -0.97 / -1.00 | PF 0.29, -0.8R (3 lệnh) | PF 0.08, -4.0R (6 lệnh) |
| 2.5× | 41 / 51 | 19.5% / 17.6% | **1.12** / **0.93** | +0.076 / -0.045R | +3.1 / -2.3R | -12.1 / -13.7R | **0.26** / **-0.17** | PF 0.29, -0.7R (3 lệnh) | PF 0.07, -3.5R (6 lệnh) |
| 3.0× | 41 / 51 | 19.5% / 17.6% | 1.05 / 0.86 | +0.026 / -0.081R | +1.1 / -4.1R | -10.4 / -11.9R | 0.10 / -0.34 | PF 0.29, -0.6R (3 lệnh) | PF 0.07, -3.2R (6 lệnh) |
| 3.5× | 41 / 51 | 19.5% / 17.6% | 1.05 / 0.84 | +0.023 / -0.080R | +0.9 / -4.1R | -9.3 / -10.7R | 0.10 / -0.38 | PF 0.29, -0.5R (3 lệnh) | PF 0.06, -3.1R (6 lệnh) |
| 4.0× | 41 / 51 | 19.5% / 17.6% | 1.00 / 0.84 | +0.002 / -0.068R | +0.1 / -3.5R | -8.5 / -9.9R | 0.01 / -0.35 | PF 0.29, -0.4R (3 lệnh) | PF 0.08, -2.0R (6 lệnh) |

##### BTC/USDT — D1 (Pullback V5)

| ATR | Lệnh A / B | Win rate A / B | PF A / B | Kỳ vọng A / B | Tổng R A / B | Max DD A / B | R/DD A / B | Ngoài mẫu A | Ngoài mẫu B |
|---|---|---|---|---|---|---|---|---|---|
| 1.0× | 7 / 8 | 14.3% / 25.0% | 1.97 / 6.23 | +0.854 / +4.019R | +6.0 / +32.1R | -4.1 / -4.1R | 1.46 / 7.83 | – | – |
| 1.5× | 7 / 8 | 14.3% / 25.0% | 1.33 / 4.19 | +0.283 / +2.429R | +2.0 / +19.4R | -4.1 / -4.1R | 0.49 / 4.78 | – | – |
| 2.0× | 7 / 8 | 28.6% / 37.5% | **2.90** / **5.49** | +1.373 / +2.837R | +9.6 / +22.7R | -2.0 / -2.0R | **4.75** / **11.21** | – | – |
| 2.5× | 7 / 8 | 28.6% / 37.5% | 2.84 / 5.37 | +1.085 / +2.258R | +7.6 / +18.1R | -2.0 / -2.0R | 3.76 / 8.95 | – | – |
| 3.0× | 7 / 8 | 42.9% / 50.0% | 3.46 / 6.42 | +1.030 / +1.992R | +7.2 / +15.9R | -2.0 / -2.0R | 3.58 / 7.91 | – | – |
| 3.5× | 7 / 8 | 42.9% / 50.0% | 3.31 / 6.17 | +0.868 / +1.694R | +6.1 / +13.6R | -1.8 / -1.8R | 3.31 / 7.39 | – | – |
| 4.0× | 7 / 8 | 42.9% / 50.0% | 3.14 / 5.85 | +0.742 / +1.467R | +5.2 / +11.7R | -1.7 / -1.7R | 3.00 / 6.78 | – | – |

##### Vàng PAXG/USDT — H1 (Pullback V5)

| ATR | Lệnh A / B | Win rate A / B | PF A / B | Kỳ vọng A / B | Tổng R A / B | Max DD A / B | R/DD A / B | Ngoài mẫu A | Ngoài mẫu B |
|---|---|---|---|---|---|---|---|---|---|
| 1.0× | 203 / 274 | 9.4% / 11.3% | 0.39 / 0.47 | -0.725 / -0.607R | -147.2 / -166.3R | -166.2 / -184.9R | -0.89 / -0.90 | PF 1.30, +10.5R (28 lệnh) | PF 1.26, +10.2R (32 lệnh) |
| 1.5× | 192 / 259 | 18.2% / 18.5% | 1.42 / 1.18 | +0.369 / +0.161R | +70.8 / +41.7R | -75.7 / -98.5R | 0.94 / 0.42 | PF 5.17, +107.4R (28 lệnh) | PF 4.68, +106.5R (32 lệnh) |
| 2.0× | 188 / 255 | 22.3% / 23.1% | 1.39 / 1.25 | +0.285 / +0.182R | +53.6 / +46.4R | -58.7 / -77.6R | 0.91 / 0.60 | PF 5.20, +83.0R (28 lệnh) | PF 5.79, +99.4R (32 lệnh) |
| 2.5× | 182 / 247 | 26.4% / 26.7% | 1.50 / 1.37 | +0.294 / +0.220R | +53.6 / +54.2R | -37.4 / -53.9R | 1.44 / 1.01 | PF 5.15, +66.2R (27 lệnh) | PF 5.73, +79.4R (31 lệnh) |
| 3.0× | 181 / 246 | 26.5% / 26.8% | 1.45 / 1.31 | +0.231 / +0.161R | +41.9 / +39.6R | -32.3 / -48.7R | 1.29 / 0.81 | PF 4.86, +54.4R (27 lệnh) | PF 5.43, +65.4R (31 lệnh) |
| 3.5× | 180 / 244 | 27.8% / 28.3% | **1.56** / **1.40** | +0.236 / +0.173R | +42.6 / +42.3R | -21.7 / -33.9R | **1.96** / **1.25** | PF 4.73, +46.3R (27 lệnh) | PF 5.28, +55.7R (31 lệnh) |
| 4.0× | 180 / 244 | 27.8% / 28.3% | 1.55 / 1.37 | +0.203 / +0.143R | +36.5 / +34.9R | -18.9 / -30.9R | 1.93 / 1.13 | PF 4.57, +40.1R (27 lệnh) | PF 5.12, +48.3R (31 lệnh) |

##### Vàng PAXG/USDT — H4 (Pullback V5)

| ATR | Lệnh A / B | Win rate A / B | PF A / B | Kỳ vọng A / B | Tổng R A / B | Max DD A / B | R/DD A / B | Ngoài mẫu A | Ngoài mẫu B |
|---|---|---|---|---|---|---|---|---|---|
| 1.0× | 42 / 59 | 26.2% / 25.4% | 1.64 / 2.79 | +0.504 / +1.440R | +21.2 / +85.0R | -9.2 / -9.7R | 2.29 / 8.77 | PF 4.22, +14.3R (6 lệnh) | PF 2.79, +12.0R (8 lệnh) |
| 1.5× | 41 / 58 | 34.1% / 34.5% | 1.77 / 2.67 | +0.503 / +1.096R | +20.6 / +63.6R | -8.3 / -10.1R | 2.50 / 6.31 | PF 2.91, +8.2R (6 lệnh) | PF 1.93, +6.0R (8 lệnh) |
| 2.0× | 40 / 56 | 40.0% / 39.3% | **2.50** / 3.16 | +0.766 / +1.120R | +30.6 / +62.7R | -4.1 / -6.5R | **7.42** / 9.58 | PF 2.33, +5.3R (6 lệnh) | PF 1.52, +3.2R (8 lệnh) |
| 2.5× | 40 / 55 | 45.0% / 45.5% | 2.79 / 3.57 | +0.707 / +1.004R | +28.3 / +55.2R | -3.9 / -4.5R | 7.24 / 12.29 | PF 2.19, +4.1R (6 lệnh) | PF 1.35, +2.0R (8 lệnh) |
| 3.0× | 40 / 55 | 45.0% / 45.5% | 2.72 / **3.66** | +0.581 / +0.844R | +23.2 / +46.4R | -3.7 / -3.7R | 6.30 / **12.59** | PF 1.96, +3.1R (6 lệnh) | PF 1.28, +1.4R (8 lệnh) |
| 3.5× | 40 / 55 | 45.0% / 45.5% | 2.78 / 3.55 | +0.504 / +0.715R | +20.2 / +39.3R | -2.7 / -3.6R | 7.36 / 10.96 | PF 1.77, +2.3R (6 lệnh) | PF 1.17, +0.8R (8 lệnh) |
| 4.0× | 40 / 55 | 45.0% / 45.5% | 2.68 / 3.50 | +0.432 / +0.622R | +17.3 / +34.2R | -2.5 / -3.3R | 6.96 / 10.29 | PF 1.62, +1.8R (6 lệnh) | PF 1.11, +0.5R (8 lệnh) |

##### Vàng PAXG/USDT — D1 (Pullback V5)

| ATR | Lệnh A / B | Win rate A / B | PF A / B | Kỳ vọng A / B | Tổng R A / B | Max DD A / B | R/DD A / B | Ngoài mẫu A | Ngoài mẫu B |
|---|---|---|---|---|---|---|---|---|---|
| 1.0× | 10 / 12 | 20.0% / 25.0% | 3.93 / 3.68 | +2.495 / +2.145R | +25.0 / +25.7R | -4.3 / -5.4R | 5.83 / 4.80 | PF 0.00, -1.0R (1 lệnh) | PF 0.00, -1.0R (1 lệnh) |
| 1.5× | 9 / 11 | 33.3% / 36.4% | 4.75 / 4.19 | +2.386 / +1.970R | +21.5 / +21.7R | -2.6 / -3.6R | 8.28 / 5.94 | PF ∞, +4.9R (1 lệnh) | PF ∞, +4.9R (1 lệnh) |
| 2.0× | 8 / 10 | 50.0% / 50.0% | **6.42** / 5.01 | +2.043 / +1.624R | +16.3 / +16.2R | -2.0 / -3.0R | **8.31** / 5.40 | PF ∞, +3.7R (1 lệnh) | PF ∞, +3.7R (1 lệnh) |
| 2.5× | 8 / 10 | 50.0% / 50.0% | 5.82 / 4.40 | +1.604 / +1.254R | +12.8 / +12.5R | -1.6 / -2.7R | 7.91 / 4.73 | PF ∞, +2.9R (1 lệnh) | PF ∞, +2.9R (1 lệnh) |
| 3.0× | 8 / 10 | 50.0% / 50.0% | 5.42 / 4.66 | +1.315 / +1.062R | +10.5 / +10.6R | -1.4 / -1.9R | 7.79 / 5.67 | PF ∞, +2.4R (1 lệnh) | PF ∞, +2.4R (1 lệnh) |
| 3.5× | 8 / 10 | 50.0% / 50.0% | 6.93 / **5.67** | +1.184 / +0.955R | +9.5 / +9.6R | -1.2 / -1.6R | 8.17 / **5.95** | PF ∞, +2.1R (1 lệnh) | PF ∞, +2.1R (1 lệnh) |
| 4.0× | 8 / 10 | 50.0% / 50.0% | 6.93 / 5.67 | +1.036 / +0.836R | +8.3 / +8.4R | -1.0 / -1.4R | 8.17 / 5.95 | PF ∞, +1.8R (1 lệnh) | PF ∞, +1.8R (1 lệnh) |

**Lệnh chỉ bộ lọc B mới có** (Pullback, phân tích theo ngày vào lệnh):

| Cấu hình | Lệnh chung A và B | Lệnh chỉ có ở B | Lệnh chỉ B: trong mẫu | Lệnh chỉ B: ngoài mẫu | Bỏ 5 lệnh lớn nhất: A / B |
|---|---|---|---|---|---|
| BTC H1 2.5× | 155 lệnh, +80.8R, PF 1.86 | 65 lệnh, +22.3R, PF 1.58 | 52 lệnh, PF 1.98 | **13 lệnh, -6.5R, PF 0.29** | -24.6R PF 0.75 / -1.0R PF 0.99 |
| Vàng H4 2.5× | 38 lệnh, +30.4R, PF 3.23 | 17 lệnh, +24.8R, PF 4.16 | 15 lệnh, PF 5.70 | **2 lệnh, -2.1R** | -0.4R PF 0.98 / +5.6R PF 1.26 |
| Vàng H4 3.0× | 38 lệnh, +25.4R, PF 3.23 | 17 lệnh, +21.1R, PF 4.46 | 15 lệnh, PF 6.15 | **2 lệnh, -1.7R** | -0.7R PF 0.95 / +5.1R PF 1.29 |

**Kết luận bộ lọc B cho Pullback:**
- **BTC H1: B tốt hơn trên toàn giai đoạn** — thêm ~57 lệnh, tổng R 2.5× từ +79.4R lên +103.1R với Max DD gần như không đổi (-13.1R), R/DD 6.06 → 7.90, và ít phụ thuộc lệnh lớn hơn (bỏ 5 lệnh lớn nhất: B còn hòa vốn, A lỗ -24.6R). Nhưng **ngoài mẫu B kém hơn** (2.5×: PF 0.70, -7.2R / 40 lệnh so với A 0.95, -0.7R / 27 lệnh) vì 13 lệnh mới thêm từ 10/2025 thua gần hết (PF 0.29).
- **Vàng H4: B tốt hơn rõ** — PF 3.2–3.7 so với 2.5–2.8 ở 2.0–4.0×, tổng R gần gấp đôi (2.5×: +55.2R so với +28.3R), Max DD tương đương, bỏ 5 lệnh lớn nhất vẫn lãi (PF 1.26). Ngoài mẫu B chỉ 8 lệnh (2 lệnh mới đều thua) — chưa đủ để xác nhận.
- **BTC H4 và vàng H1: B kém hơn** (BTC H4 Pullback lỗ ở mọi mức ATR với B; vàng H1 B có DD sâu hơn hẳn, -54R so với -37R ở 2.5×).
- **D1**: B cho PF cao hơn ở BTC (5–6 so với 2–3) nhưng chỉ 8 lệnh, không có ý nghĩa thống kê.
- **BTC 15m: B kém hơn ở mọi mức ATR** (`results/ema9_45_btc_15m.csv`, `results/ema9_45_locB_btc_15m.csv`): Pullback 2.5× A 770 lệnh PF 1.07, +36.5R, DD -45.6R so với B 983 lệnh PF 1.00, +3.6R, DD -58.9R; ngoài mẫu A PF 0.65 (-31.3R) so với B 0.59 (-48.2R). Pullback 15m vốn đã không có lợi thế, B còn làm tệ hơn.
- Tóm lại: bộ lọc B (vào sớm hơn khi xu hướng mới hình thành, EMA45 chưa kịp vượt EMA200) **giúp Pullback ở BTC H1 và vàng H4 trên dữ liệu quá khứ**, nhưng các lệnh thêm vào đều thua trong giai đoạn ngoài mẫu (mẫu nhỏ). Nếu dùng B, nên theo dõi thêm và giữ rủi ro nhỏ.

**Trên TradingView (17/10/2026):** script "EMA9/45/200 Breakout & Pullback V5" (bản đang dùng, phiên bản 10) có thêm ô **"Bộ lọc xu hướng cho Pullback"** — mặc định **"Giá > EMA200"** (bộ lọc B), chọn "EMA9 > EMA45 > EMA200" để quay về bộ lọc A; Breakout luôn dùng bộ lọc A. Sửa bằng 2 thay đổi: thêm input `pbFilter` và `bool trendOK = mode != "Breakout" and pbFilter == "Giá > EMA200" ? close > e200 : e45 > e200`, `aligned = e9 > e45 and trendOK and ...` — mọi chỗ dùng `aligned` (nến cắt lên, nến tín hiệu Pullback, điều kiện đặt lệnh, dấu ▲) tự áp bộ lọc mới, giống backtest Python. Các phần riêng của bản trên TradingView (đòn bẩy tối đa, ký quỹ 10x, tự theo dõi vị thế) giữ nguyên. Theo kết quả trên: nên dùng B cho Pullback **BTC H1 và vàng H4**, đổi về A cho **BTC H4, vàng H1 và 15m**.

## Chiến lược trên TradingView (28/9/2026)

File `tradingview/ema_9_45_200_trend_strategy_vi.pine` (bản tiếng Anh: `ema_9_45_200_trend_strategy.pine`) là strategy **Pine Script v6** chuyển từ backtest Python, dùng đúng luật hiện hành: lọc EMA9 > EMA45 > EMA200, bỏ qua 200 nến đầu (làm nóng EMA), EMA khởi tạo từ giá đầu tiên giống `pandas ewm(adjust=False)`, ATR(14) = EMA của true range, lệnh chờ mua (stop) ở đỉnh nến tín hiệu, lệnh chờ tự hủy khi EMA9 cắt xuống EMA45, SL = giá vào - k×ATR, thoát bằng lệnh chờ bán ở đáy nến EMA9 cắt xuống (hủy nếu EMA9 cắt lên lại).

**Cài đặt (Settings của strategy):**

| Thông số | Mặc định | Ghi chú |
|---|---|---|
| Kiểu vào lệnh | Breakout | Hoặc Pullback V5 |
| SL = k × ATR(14) | 2.5 | BTC H1 Breakout 2.5; vàng H4 Breakout 2.0–3.5 hoặc Pullback V5 2.0–2.5 |
| Rủi ro mỗi lệnh | 1% vốn | Khối lượng = vốn × rủi ro / khoảng SL |
| EMA nhanh / chậm / xu hướng | 9 / 45 / 200 | |
| Số nến làm nóng EMA | 200 | |
| Chỉ vào lệnh từ ngày | 2021-01-01 | |

Strategy dùng vốn khởi đầu $1,000 và phí 0.04%/chiều. Trên biểu đồ hiển thị 3 đường EMA, mức chờ mua (xanh lá), **SL dự kiến** (đỏ nhạt = mức chờ mua − k×ATR, hiện ngay khi có lệnh chờ), stop loss (đỏ, khi đang giữ lệnh), mức chờ thoát (tím hồng) và dấu tín hiệu cắt lên/cắt xuống. Các mức được vẽ bằng chấm tròn, nên mức chỉ tồn tại 1 nến (lệnh chờ khớp ngay nến sau, hoặc khớp rồi chạm SL ngay trong nến) vẫn nhìn thấy; trường hợp khớp rồi chạm SL cùng nến vẫn có chấm SL ở nến đó. Ở nến cuối cùng, các mức đang có hiệu lực được vẽ thêm bằng đường nét đứt kéo sang phải kèm nhãn giá (vì `plot()` cần 2 nến mới vẽ được đường, nên mức mới xuất hiện ở nến cuối sẽ không hiện nếu chỉ dùng `plot()`). Giá trị ATR(14) và khoảng SL (k×ATR) xem trong Data Window. Lưu ý: ATR của script là EMA của true range (giống backtest Python), khác chỉ báo ATR mặc định của TradingView (RMA/Wilder), nên tự nhân ATR của TradingView × 2.5 sẽ ra số hơi khác.

### Đọc biểu đồ và vào lệnh thủ công (cập nhật 3/10/2026)

| Trên biểu đồ | Ý nghĩa | Khi nào hiện |
|---|---|---|
| ▲ xanh dưới nến | Tín hiệu: EMA9 cắt lên EMA45, 3 EMA xếp đúng thứ tự | Nến tín hiệu |
| Chấm **xanh lá** + nhãn **"Buy stop …"** | **Giá entry**: đặt lệnh stop mua ở đây | Từ khi nến tín hiệu đóng đến khi khớp hoặc bị hủy |
| Chấm **đỏ nhạt** + nhãn **"Projected SL …"** | **SL dự kiến** = Buy stop − 2.5×ATR | Cùng lúc với Buy stop |
| Mũi tên **"Long"** | Lệnh đã khớp (giá vào thực tế) | Nến khớp lệnh |
| Chấm **đỏ đậm** + nhãn **"Stop loss …"** | **SL thật** = giá khớp − 2.5×ATR | Suốt thời gian giữ lệnh, kể cả lệnh khớp rồi chạm SL ngay trong nến |
| Chấm **tím hồng** + nhãn **"Exit stop …"** | Mức thoát (đáy nến EMA9 cắt xuống) | Khi đang giữ lệnh và EMA9 vừa cắt xuống |
| Mũi tên **"Exit"** | Lệnh đã đóng | Nến thoát lệnh |

Ở nến mới nhất, các mức đang hiệu lực được vẽ thêm bằng nét đứt kéo sang phải kèm nhãn giá; khoảng SL và ATR xem trong **Data Window**. (Bản tiếng Việt dùng nhãn "Chờ mua", "SL dự kiến", "Stop loss", "Chờ thoát".)

Quy trình khi tự theo dõi biểu đồ (gói TradingView miễn phí không có alert kỹ thuật):
1. Khi thấy "Buy stop" và "Projected SL": đặt **lệnh stop mua** ở Buy stop và **SL** ở Projected SL trên sàn. Khối lượng = (vốn thật × % rủi ro) ÷ khoảng SL (khối lượng trong script dựa trên vốn giả lập $1,000, không dùng được cho tài khoản thật).
2. Nếu đường xanh biến mất trước khi khớp (EMA9 cắt xuống): **hủy lệnh chờ** trên sàn.
3. Khi đã khớp: SL thật = **giá khớp thực tế − khoảng SL** (nếu nến mở cửa vượt mức chờ thì giá khớp cao hơn Buy stop, SL cũng dịch lên) — đúng bằng chấm đỏ đậm hiện sau khi khớp.
4. Khi xuất hiện "Exit stop": dời lệnh dừng trên sàn lên mức đó nếu nó cao hơn SL (mức cao hơn bị chạm trước); nếu EMA9 cắt lên lại thì trả về SL cũ.
5. Các mức chỉ cập nhật **khi nến 1h đóng cửa**; script **không tự đặt lệnh** trên sàn.

Đã kiểm tra trên BTCUSDT 1h: tín hiệu Buy stop 85,514 / SL dự kiến 84,108.27 hiện chấm ở nến tín hiệu; nến sau khớp rồi chạm SL cùng giờ, có chấm Stop loss 84,108.29. Chưa kiểm tra trực tiếp được đường nét đứt + nhãn ở nến mới nhất (chưa có lệnh chờ/lệnh mở kể từ khi sửa).

**Cảnh báo (alert):** script gửi cảnh báo khi nến đóng cửa cho 7 sự kiện: có lệnh chờ mua mới (kèm giá chờ, SL dự kiến, khoảng SL), hủy lệnh chờ mua, đã khớp mua (kèm SL), khớp rồi chạm SL ngay trong nến, có mức chờ thoát (kèm mức dừng hiệu lực), hủy lệnh chờ thoát, đã đóng lệnh. Cách bật: trên biểu đồ bấm **Alert** (biểu tượng đồng hồ) → Condition chọn strategy này → chọn **"alert() function calls only"** → chọn cách nhận (app, email…) → Create. Cả 7 sự kiện nằm trong 1 alert. Mỗi lần sửa script phải xóa và tạo lại alert (alert chạy trên bản script lúc tạo). **Lưu ý:** alert trên chỉ báo/strategy cần gói TradingView trả phí; gói Basic miễn phí cho 0 alert kỹ thuật (đã thử ngày 3/10/2026: "Alert saving failed" + yêu cầu nâng cấp).

**Cách dùng:** mở TradingView → Pine Editor → dán nội dung file → **Add to chart** → xem tab **Strategy Tester**. Script đã được lưu riêng tư trong tài khoản TradingView của chủ dự án với tên **"EMA9/45/200 Breakout & Pullback V5"** (mở lại trong Pine Editor → Open, hoặc Indicators → My scripts). Cảnh báo (alert) trên strategy cần gói trả phí, xem mục cảnh báo ở trên.

**Kiểm tra trên TradingView (28/9/2026)**: script biên dịch không lỗi. BTCUSDT (Binance) H1, Breakout, SL 2.5×ATR, rủi ro 1%/lệnh:

| | TradingView (1/1 → 28/9/2026) | Backtest Python (lệnh vào 1/1 → 23/9/2026) |
|---|---|---|
| Số lệnh | 20 | 24 |
| Win rate | 45.0% | 41.7% |
| PF (sau phí 0.04%) | 1.26 | 1.33 |
| Lãi / Max DD | +$24.38 (+2.4%) / -6.6% | – |

Hai kết quả gần nhau. Chênh lệch chủ yếu do tài khoản TradingView miễn phí chỉ tải dữ liệu H1 từ khoảng cuối 2025, nên EMA200 bắt đầu tính muộn và giai đoạn làm nóng 200 nến bỏ lỡ vài lệnh đầu tháng 1/2026. Chưa đối chiếu được từng lệnh (danh sách lệnh chi tiết bị giới hạn ở gói miễn phí).

**Khác biệt so với backtest Python:**
- TradingView chỉ tải một số nến lịch sử giới hạn (tùy gói tài khoản), nên kết quả chỉ phản ánh giai đoạn ngắn và điểm bắt đầu EMA khác backtest.
- SL chạm ngay trong nến vào lệnh do bộ giả lập của TradingView quyết định theo OHLC (hoặc Bar Magnifier nếu bật), không phải giả định bất lợi / nến H1 như lưu ý #9.
- Khi SL và mức thoát breakdown cùng bị chạm trong một nến, script thoát ở mức cao hơn (mức giá chạm trước), còn backtest Python ưu tiên SL.

**Bản tiếng Anh để đăng công khai (mã nguồn mở, MPL 2.0):** `tradingview/ema_9_45_200_trend_strategy.pine` (logic giống hệt bản tiếng Việt, nhãn và input bằng tiếng Anh) cùng mô tả `mô tả đăng bài`. Script đã được lưu riêng tư trong tài khoản với tên **"EMA 9/45/200 Trend Strategy [Breakout / Pullback]"**. **Chưa đăng công khai được** (28/9/2026): TradingView chỉ cho tài khoản **gói trả phí** đăng script lên Community Scripts (gói Basic và gói dùng thử đều bị chặn). Khi có gói trả phí: mở script trong Pine Editor → **Publish script** → dán mô tả → Public + Open → danh mục *Trend analysis* → Publish. Bản nháp đăng bài đang được thu nhỏ trong Pine Editor.

**Mã nguồn mở trên GitHub (28/9/2026):** https://github.com/thangchelseakt95-boop/ema-9-45-200-trend-strategy (Public, MPL 2.0). Repo gồm README tiếng Anh, file Pine (tiếng Anh + tiếng Việt), toàn bộ script Python, dữ liệu `data/`, `results/` và bản README này ở `docs/research-notes-vi.md`.

## Kết luận tổng hợp (cập nhật 28/9/2026)

> **BTC: H1 + Breakout + SL 2.5×ATR. Vàng (PAXG): H4, với Breakout 2.0–3.5× hoặc Pullback V5 2.0–2.5×.** Các khung và cách vào lệnh còn lại không có lợi thế đáng tin. Số liệu toàn giai đoạn 2021-01 → 2026-09, **sau phí 0.04%/chiều**, đã kiểm chứng bằng engine độc lập (lưu ý #13, #14) và đối chiếu tự động với các bảng trong README.

### 1. BTC theo khung thời gian

| Khung | Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Max DD | Ngoài mẫu (sau 30/9/2025) | Đánh giá |
|---|---|---|---|---|---|---|---|---|---|
| **H1** | **Breakout** | **2.5×** | 205 | 28.3% | **1.84** | +0.533R | -15.3R | PF 1.18 (28 lệnh) | **Dùng** |
| H1 | Pullback V5 | 2.5× | 159 | 26.4% | 1.84 | +0.504R | -13.1R | PF 1.15 (23 lệnh) | Phương án phụ |
| H4 | Breakout | 2.0× | 60 | 21.7% | 1.46 | +0.307R | -10.8R | Thua cả 7 lệnh | Không dùng |
| D1 | Breakout | 2.5× | 11 | 45.5% | 2.96 | +0.848R | -2.0R | 1 lệnh, thua | Thiếu dữ liệu |

- **H1**: mẫu lớn, lãi ổn định ở mọi mức ATR, vẫn lãi trên dữ liệu mới. Breakout lãi nhiều hơn Pullback V5 ~35% (+109R so với +80R); V5 DD nhẹ hơn nhưng lỗ ngoài mẫu ở ATR 1.5–2.0×.
- **H4**: lãi chỉ nhờ 2 lệnh lớn (lưu ý #11), thua cả 7 lệnh ngoài mẫu.
- **D1**: chỉ 7–11 lệnh trong gần 6 năm, không có ý nghĩa thống kê.

### 2. Vàng (PAXG/USDT) theo khung thời gian

| Khung | Chiến lược | ATR | Lệnh | Win rate | PF | Kỳ vọng | Max DD | Ngoài mẫu (sau 30/9/2025) | Đánh giá |
|---|---|---|---|---|---|---|---|---|---|
| **H4** | **Breakout** | 2.0× | 56 | 37.5% | 2.51 | +0.740R | -6.5R | PF 6.2 (8 lệnh) | **Dùng** |
| **H4** | **Pullback V5** | 2.5× | 40 | 45.0% | **2.79** | +0.707R | **-3.9R** | PF 2.35 (6 lệnh) | **Dùng** (DD thấp hơn) |
| H1 | Breakout | 4.0× | 214 | 35.0% | 1.53 | +0.196R | -19.3R | – | Không (vỡ khi phí 0.1%) |
| D1 | Breakout | 2.5× | 11 | 54.5% | 9.75 | +3.45R | -1.7R | 0 lệnh | Thiếu dữ liệu |

- **H4**: lãi phân bố đều hơn BTC (bỏ 3 lệnh lớn nhất vẫn còn lãi), vẫn giữ PF trên 2 khi phí 0.1%.
- **Lưu ý**: vàng tăng rất mạnh trong giai đoạn test ($1,835 → ~$4,300), thanh khoản PAXG mỏng, và PAXG khác vàng giao ngay (giao dịch cả cuối tuần). Chi tiết ở mục "Vàng (PAXG/USDT)".

### 3. Breakout so với Pullback V5

| Tài sản / khung | Bên thắng |
|---|---|
| BTC H1 | **Breakout** — cùng PF nhưng lãi nhiều hơn, bền hơn ngoài mẫu |
| BTC H4 | Breakout, nhưng cả hai đều không nên dùng |
| Vàng H4 | **Ngang nhau** — Breakout lãi nhiều hơn và ngoài mẫu tốt hơn, Pullback V5 DD nhẹ hơn |

Pullback V5 (nhận cả kiểu "chạm rồi bật" và "cắt xuống rồi cắt lại") tốt hơn luật Pullback cũ V1 nên được đặt làm mặc định (lưu ý #14). Chi tiết ở mục "So sánh Breakout vs Pullback V5 theo từng khung".

### 4. Bộ lọc xu hướng: EMA9 > EMA45 > EMA200 (A, đang dùng) so với EMA9 > EMA45 và giá > EMA200 (B)

| Cấu hình | A: PF / tổng R / Max DD / ngoài mẫu | B: PF / tổng R / Max DD / ngoài mẫu |
|---|---|---|
| BTC H1 2.5× | **1.84** / +109.2R / **-15.3R** / **PF 1.18** (28 lệnh) | 1.67 / **+125.5R** / -17.0R / PF 0.79 (48 lệnh) |
| BTC H4 2.0× | 1.46 / +18.4R / **-10.8R** / thua cả 7 lệnh | **1.70** / **+35.3R** / -13.6R / **PF 2.04** (12 lệnh, thắng 1) |
| Vàng H4 2.5× | 2.43 / +32.4R / **-4.6R** / **PF 6.23** (8 lệnh) | **2.71** / **+56.3R** / -5.6R / PF 5.33 (10 lệnh) |

- **H1**: bộ lọc A tốt hơn rõ — B thêm ~100 lệnh chất lượng kém (BTC H1: 107 lệnh chỉ có ở B, PF 1.24) và BTC H1 lỗ ngoài mẫu với B.
- **H4**: B cho lãi nhiều hơn vì bắt xu hướng sớm hơn (trước khi EMA45 kịp vượt EMA200), nhưng dựa vào vài lệnh lớn (BTC H4: ngoài mẫu chỉ thắng 1/12 lệnh) và DD sâu hơn. Chưa đổi bộ lọc mặc định — coi đây là giả thuyết cần theo dõi thêm.

### 5. Hybrid so với chỉ trade theo tín hiệu (vốn $1,000, BTC H1 Breakout 2.5×, rủi ro 1%/lệnh, phí 0.04%/chiều, lãi vay USDT 3.5%/năm)

| Hệ thống | Giá trị cuối | Nhân vốn | Max DD |
|---|---|---|---|
| Chỉ trade theo tín hiệu (không giữ BTC, không đòn bẩy) | $2,274 | x2.27 (~15%/năm) | **-17.3%** |
| **Hybrid** (giữ BTC mua từ đầu + margin vay USDT theo tín hiệu) | **$4,267** | **x4.27** (~29%/năm) | -80.2% |
| Buy & Hold | $2,897 | x2.90 (~20%/năm) | -77.2% |

Hybrid lãi nhiều nhất (phần margin đóng góp $1,370, đã trả ~$78 lãi vay) nhưng DD còn sâu hơn Buy & Hold, và phần lớn lợi nhuận đến từ việc giữ BTC. Chọn Hybrid hay trade thuần tùy mức DD chịu được. Với tín hiệu mua, vay USDT là cách đúng (vay BTC để mua thì vị thế ròng bằng 0); vay BTC chỉ có ý nghĩa để phòng hộ phần BTC đang giữ khi tín hiệu báo giảm — chưa backtest. Mô phỏng này chưa tính thanh lý và trượt giá; bảng "So sánh chiến lược" (vốn 1 BTC, đến 30/9/2025, ATR 2.0×) ở trên dùng cấu hình khác nên số không giống.

### 6. Bài học từ quá trình kiểm tra

- **Backtest ban đầu quá lạc quan** vì bốn lỗi: lệch 1 nến khi xét breakout (lưu ý #8), khớp lệnh ở giá không có thật (lưu ý #8, #11), bỏ qua SL chạm ngay trong nến vào lệnh (lưu ý #9), EMA chưa hội tụ ở đầu dữ liệu (lưu ý #12). Sửa xong, vd. BTC H4 từ PF 2.44 xuống 1.75 (cùng dữ liệu 2021–9/2025).
- **Số càng đẹp càng phải nghi ngờ**: PF 3 trở lên với ít lệnh (D1) thường là may mắn.
- **Kiểm tra ngoài mẫu là bắt buộc**: nhiều cấu hình đẹp trên dữ liệu cũ đã mất lợi thế trên dữ liệu mới (vd. Pullback H1 ở ATR thấp).

### 7. Những gì chưa chắc chắn

1. **Trượt giá chưa tính** — rủi ro lớn với PAXG vì thanh khoản mỏng.
2. **Nguy cơ overfitting**: đã thử nhiều mức ATR, 2 bộ lọc và 5 biến thể Pullback trên cùng một bộ dữ liệu.
3. **Mẫu ngoài mẫu nhỏ**: BTC H1 ~28 lệnh, vàng H4 chỉ 6–8 lệnh.
4. **Giai đoạn test thuận lợi cho chiến lược đi theo xu hướng**: cả BTC và vàng đều tăng mạnh.
5. **H1 dùng giả định bất lợi** cho SL trong nến vào lệnh (không có dữ liệu nến nhỏ hơn).
6. Số liệu **DCA và Full-capital EMA9/45** trong bảng "So sánh chiến lược" vẫn tính bằng code cũ trước khi sửa lỗi, chưa tính lại.

### 8. Khuyến nghị

1. **BTC**: H1 + Breakout + SL 2.5×ATR (Pullback V5 2.5× là phương án phụ nếu ưu tiên DD thấp hơn).
2. **Vàng**: H4 + Breakout 2.0–3.5×, hoặc Pullback V5 2.0–2.5× nếu ưu tiên DD thấp.
3. **Không dùng**: BTC H4, D1 của cả hai tài sản, vàng H1.
4. **Rủi ro nhỏ mỗi lệnh (0.5–1% vốn)**: win rate chỉ ~25–45%, sẽ có chuỗi thua 10 lệnh trở lên.
5. **Chạy thử bằng tài khoản ảo hoặc lệnh rất nhỏ trước**; chạy lại `oos_test.py`, `oos_pullback_test.py` và `asset_test.py` định kỳ khi có dữ liệu mới.
6. **Dừng lại xem xét** nếu PF ngoài mẫu tụt dưới 1.0 sau khoảng 50 lệnh.

> Đây là kết quả kiểm định trên dữ liệu lịch sử, không phải tư vấn tài chính và không đảm bảo lợi nhuận trong tương lai.

## Việc còn dang dở / có thể làm tiếp
- Test thêm biến thể: risk % khác cho phần margin trong Hybrid, lãi suất vay khác, hoặc kết hợp EMA200 filter chéo khung (vd. lọc bằng EMA200 khung D1 khi trade H4).
- Vàng (PAXGUSDT) đã làm (xem mục "Vàng"). Có thể thử thêm XAU/USD giao ngay để so với PAXG, và áp dụng `asset_test.py` cho NVDA, AAPL với logic đã sửa lỗi (các kết quả cũ cho những tài sản này trong phiên trước đều dùng logic cross_up/cross_down có lỗi, nên không còn đáng tin).
- `backtest_h4_2atr.py` là script cũ (bộ lọc giá > EMA200), chưa áp dụng luật tự hủy lệnh chờ và bản sửa lệch 1 nến — nên cập nhật hoặc xóa để tránh nhầm lẫn.
- Khung H1 vẫn dùng giả định bất lợi cho SL trong nến vào lệnh (lưu ý #9); nếu tải thêm dữ liệu M5/M15 từ data.binance.vision có thể xử lý chính xác tương tự H4/D1.
