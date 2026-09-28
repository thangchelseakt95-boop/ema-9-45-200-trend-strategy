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
  paxg_h1.csv, paxg_h4.csv -> Vàng PAXG/USDT H1/H4, 2021-01-01 -> 2026-09-27, tải bằng download_binance.py (chỉ nến đã đóng)
scripts/
  backtest_main.py      -> Chạy backtest chính (breakout entry, breakdown exit, SL=2xATR) cho cả D1/H4/H1 + mô hình Hybrid, kết thúc 30/9/2025
  backtest_h4_2atr.py   -> Backtest H4 riêng, SL=2xATR
  pullback_test.py      -> So sánh Breakout entry vs Pullback entry (Pullback V5 mặc định, variant='v1' cho luật cũ)
  oos_test.py           -> Validation out-of-sample: warm-up từ 2025-01-01, chỉ tính lệnh vào SAU 30/9/2025
  full_track.py         -> Full track record D1/H4/H1 trên toàn bộ dữ liệu 2021 -> nay, ATR 1.0-4.0, lưu results/full_track_summary.csv
  oos_pullback_test.py  -> Validation out-of-sample cho Breakout VA Pullback (oos_test.py chỉ có Breakout)
  download_binance.py   -> Tải nến Binance (public API) cho cặp bất kỳ, lưu CSV dt,open,high,low,close,volume
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

Strategy dùng vốn khởi đầu $1,000 và phí 0.04%/chiều. Trên biểu đồ hiển thị 3 đường EMA, mức chờ mua, stop loss, mức chờ thoát và dấu tín hiệu cắt lên/cắt xuống.

**Cách dùng:** mở TradingView → Pine Editor → dán nội dung file → **Add to chart** → xem tab **Strategy Tester**. Script đã được lưu riêng tư trong tài khoản TradingView của chủ dự án với tên **"EMA9/45/200 Breakout & Pullback V5"** (mở lại trong Pine Editor → Open, hoặc Indicators → My scripts). Có thể tạo cảnh báo bằng nút **Add alert** trong Strategy Tester.

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
