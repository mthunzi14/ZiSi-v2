# Detailed Forensics: June 26 Losses

### Loss # Forensics: Detailed Analysis of Losses (June 22 - June 26, 2026)
This document compiles every single loss since June 22, detailing the asset, timeframe, direction, entry/exit prices, realized P&L, matched signal metrics, and local logs surrounding the entry event.

## Loss Summary Table
| Time (SAST) | Asset | TF | Strat | Dir | Entry | Exit | PnL ($) | Reason |
|---|---|---|---|---|---|---|---|---|
| 2026-06-22 04:35:34 | UNK | 5m | SIG | NO | 0.495 | 0.010 | -5.82 | MARKET_EXPIRED |
| 2026-06-22 04:50:29 | UNK | 5m | SIG | NO | 0.500 | 0.010 | -3.43 | MARKET_EXPIRED |
| 2026-06-22 06:05:35 | UNK | 5m | SIG | NO | 0.485 | 0.010 | -9.97 | MARKET_EXPIRED |
| 2026-06-22 07:10:16 | UNK | 5m | SIG | YES | 0.485 | 0.010 | -5.70 | MARKET_EXPIRED |
| 2026-06-22 07:10:24 | UNK | 5m | SIG | YES | 0.500 | 0.010 | -5.88 | MARKET_EXPIRED |
| 2026-06-22 08:35:36 | UNK | 5m | SIG | NO | 0.495 | 0.010 | -9.70 | MARKET_EXPIRED |
| 2026-06-22 08:35:53 | UNK | 5m | SIG | NO | 0.500 | 0.010 | -9.80 | MARKET_EXPIRED |
| 2026-06-22 10:30:20 | UNK | 5m | SIG | NO | 0.495 | 0.010 | -5.82 | MARKET_EXPIRED |
| 2026-06-22 11:30:14 | UNK | 5m | SIG | NO | 0.495 | 0.010 | -9.70 | MARKET_EXPIRED |
| 2026-06-22 14:00:24 | UNK | 15m | SIG | NO | 0.515 | 0.010 | -9.60 | MARKET_EXPIRED |
| 2026-06-22 14:30:05 | UNK | 15m | SIG | NO | 0.515 | 0.010 | -16.16 | MARKET_EXPIRED |
| 2026-06-22 15:00:10 | UNK | 15m | SIG | NO | 0.515 | 0.010 | -15.65 | MARKET_EXPIRED |
| 2026-06-22 18:45:21 | UNK | 5m | SIG | NO | 0.495 | 0.010 | -9.70 | MARKET_EXPIRED |
| 2026-06-22 19:50:17 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -5.94 | MARKET_EXPIRED |
| 2026-06-22 21:00:30 | UNK | 15m | SIG | NO | 0.495 | 0.010 | -9.70 | MARKET_EXPIRED |
| 2026-06-22 21:05:38 | UNK | 5m | SIG | NO | 0.505 | 0.010 | -5.94 | MARKET_EXPIRED |
| 2026-06-23 06:50:13 | UNK | 5m | SIG | NO | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-23 06:50:52 | UNK | 5m | SIG | NO | 0.500 | 0.010 | -9.80 | MARKET_EXPIRED |
| 2026-06-23 07:00:35 | UNK | 5m | SIG | YES | 0.540 | 0.010 | -10.07 | MARKET_EXPIRED |
| 2026-06-23 07:00:37 | UNK | 5m | REV | YES | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-23 07:45:09 | UNK | 15m | SIG | YES | 0.515 | 0.010 | -19.70 | MARKET_EXPIRED |
| 2026-06-23 08:10:29 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -11.88 | MARKET_EXPIRED |
| 2026-06-23 08:25:10 | UNK | 5m | SIG | YES | 0.515 | 0.010 | -13.63 | MARKET_EXPIRED |
| 2026-06-23 08:30:32 | UNK | 5m | SIG | YES | 0.515 | 0.010 | -13.13 | MARKET_EXPIRED |
| 2026-06-23 08:55:08 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -19.80 | MARKET_EXPIRED |
| 2026-06-23 09:45:11 | UNK | 15m | SIG | YES | 0.500 | 0.010 | -6.86 | MARKET_EXPIRED |
| 2026-06-23 10:40:08 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -19.80 | MARKET_EXPIRED |
| 2026-06-23 10:50:16 | UNK | 5m | SIG | YES | 0.515 | 0.010 | -19.70 | MARKET_EXPIRED |
| 2026-06-23 12:05:25 | UNK | 5m | SIG | NO | 0.500 | 0.010 | -5.88 | MARKET_EXPIRED |
| 2026-06-23 12:10:17 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-23 13:40:09 | UNK | 5m | SIG | NO | 0.505 | 0.010 | -19.80 | MARKET_EXPIRED |
| 2026-06-23 13:45:17 | UNK | 15m | SIG | YES | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-23 13:50:15 | UNK | 5m | SIG | NO | 0.500 | 0.010 | -6.86 | MARKET_EXPIRED |
| 2026-06-23 14:10:33 | UNK | 5m | SIG | NO | 0.500 | 0.010 | -6.86 | MARKET_EXPIRED |
| 2026-06-23 14:55:15 | UNK | 5m | SIG | YES | 0.500 | 0.010 | -11.76 | MARKET_EXPIRED |
| 2026-06-23 15:00:10 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -19.80 | MARKET_EXPIRED |
| 2026-06-23 15:10:09 | UNK | 5m | SIG | YES | 0.500 | 0.010 | -11.76 | MARKET_EXPIRED |
| 2026-06-23 15:10:25 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -19.80 | MARKET_EXPIRED |
| 2026-06-23 15:15:28 | UNK | 5m | SIG | NO | 0.495 | 0.010 | -9.70 | MARKET_EXPIRED |
| 2026-06-23 15:15:31 | UNK | 5m | SIG | NO | 0.500 | 0.010 | -9.80 | MARKET_EXPIRED |
| 2026-06-23 15:15:32 | UNK | 5m | SIG | NO | 0.500 | 0.010 | -9.80 | MARKET_EXPIRED |
| 2026-06-23 15:30:28 | UNK | 5m | SIG | YES | 0.515 | 0.010 | -19.70 | MARKET_EXPIRED |
| 2026-06-23 16:05:25 | UNK | 5m | SIG | NO | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-23 16:05:30 | UNK | 5m | SIG | NO | 0.495 | 0.010 | -9.70 | MARKET_EXPIRED |
| 2026-06-23 16:05:36 | UNK | 5m | SIG | NO | 0.520 | 0.010 | -9.69 | MARKET_EXPIRED |
| 2026-06-23 16:10:19 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-23 17:10:09 | UNK | 5m | SIG | YES | 0.500 | 0.010 | -6.86 | MARKET_EXPIRED |
| 2026-06-23 17:15:10 | UNK | 5m | SIG | NO | 0.495 | 0.010 | -9.70 | MARKET_EXPIRED |
| 2026-06-23 17:15:26 | UNK | 5m | SIG | NO | 0.495 | 0.010 | -9.70 | MARKET_EXPIRED |
| 2026-06-23 17:15:33 | UNK | 15m | SIG | NO | 0.495 | 0.010 | -9.70 | MARKET_EXPIRED |
| 2026-06-23 20:00:30 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-23 20:00:32 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-23 20:00:33 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-23 20:00:34 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-23 20:30:11 | UNK | 5m | SIG | NO | 0.495 | 0.010 | -9.70 | MARKET_EXPIRED |
| 2026-06-23 20:50:22 | UNK | 5m | REV | YES | 0.505 | 0.010 | -19.80 | MARKET_EXPIRED |
| 2026-06-23 20:50:33 | UNK | 5m | REV | YES | 0.510 | 0.010 | -19.50 | MARKET_EXPIRED |
| 2026-06-23 21:50:20 | UNK | 5m | SIG | YES | 0.510 | 0.010 | -6.00 | MARKET_EXPIRED |
| 2026-06-23 22:15:18 | UNK | 15m | SIG | YES | 0.480 | 0.010 | -5.64 | MARKET_EXPIRED |
| 2026-06-23 23:15:24 | UNK | 15m | SIG | YES | 0.495 | 0.010 | -5.82 | MARKET_EXPIRED |
| 2026-06-23 23:50:34 | UNK | 5m | SIG | YES | 0.490 | 0.010 | -9.60 | MARKET_EXPIRED |
| 2026-06-23 24:15:35 | UNK | 5m | SIG | NO | 0.500 | 0.010 | -6.86 | MARKET_EXPIRED |
| 2026-06-23 24:20:17 | UNK | 5m | SIG | NO | 0.505 | 0.010 | -11.88 | MARKET_EXPIRED |
| 2026-06-23 24:30:25 | UNK | 15m | SIG | YES | 0.490 | 0.480 | -0.12 | MARKET_EXPIRED |
| 2026-06-24 02:00:34 | UNK | 15m | SIG | YES | 0.485 | 0.010 | -9.97 | MARKET_EXPIRED |
| 2026-06-24 03:00:59 | UNK | 15m | SIG | YES | 0.485 | 0.010 | -5.70 | MARKET_EXPIRED |
| 2026-06-24 04:00:34 | UNK | 15m | SIG | YES | 0.505 | 0.010 | -7.92 | MARKET_EXPIRED |
| 2026-06-24 05:05:10 | UNK | 5m | SIG | YES | 0.525 | 0.010 | -10.81 | MARKET_EXPIRED |
| 2026-06-24 07:30:09 | UNK | 5m | SIG | NO | 0.535 | 0.010 | -13.65 | MARKET_EXPIRED |
| 2026-06-24 08:25:29 | UNK | 5m | SIG | YES | 0.575 | 0.010 | -5.65 | MARKET_EXPIRED |
| 2026-06-24 11:00:18 | UNK | 15m | SIG | YES | 0.585 | 0.010 | -6.32 | MARKET_EXPIRED |
| 2026-06-24 12:30:33 | UNK | 15m | SIG | NO | 0.585 | 0.010 | -9.78 | MARKET_EXPIRED |
| 2026-06-24 12:30:39 | UNK | 15m | SIG | NO | 0.565 | 0.010 | -9.99 | MARKET_EXPIRED |
| 2026-06-24 12:30:45 | UNK | 15m | SIG | NO | 0.485 | 0.010 | -9.97 | MARKET_EXPIRED |
| 2026-06-24 12:30:56 | UNK | 15m | SIG | NO | 0.435 | 0.010 | -9.78 | MARKET_EXPIRED |
| 2026-06-24 13:05:10 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -11.38 | MARKET_EXPIRED |
| 2026-06-24 14:55:36 | UNK | 5m | SIG | YES | 0.585 | 0.010 | -13.22 | MARKET_EXPIRED |
| 2026-06-24 15:00:09 | UNK | 5m | SIG | YES | 0.555 | 0.010 | -9.81 | MARKET_EXPIRED |
| 2026-06-24 15:10:10 | UNK | 5m | SIG | YES | 0.515 | 0.010 | -9.60 | MARKET_EXPIRED |
| 2026-06-24 15:15:10 | UNK | 5m | SIG | YES | 0.595 | 0.010 | -11.70 | MARKET_EXPIRED |
| 2026-06-24 15:45:37 | UNK | 5m | SIG | YES | 0.575 | 0.010 | -19.77 | MARKET_EXPIRED |
| 2026-06-24 15:45:44 | UNK | 5m | REV | YES | 0.635 | 0.010 | -19.38 | MARKET_EXPIRED |
| 2026-06-24 17:00:09 | UNK | 15m | SIG | YES | 0.465 | 0.010 | -14.56 | MARKET_EXPIRED |
| 2026-06-24 17:30:09 | UNK | 15m | SIG | YES | 0.415 | 0.010 | -10.12 | MARKET_EXPIRED |
| 2026-06-24 17:40:26 | UNK | 5m | SIG | YES | 0.540 | 0.010 | -11.66 | MARKET_EXPIRED |
| 2026-06-24 17:55:10 | UNK | 5m | SIG | YES | 0.560 | 0.010 | -3.85 | MARKET_EXPIRED |
| 2026-06-24 18:30:09 | UNK | 15m | SIG | YES | 0.525 | 0.010 | -11.33 | MARKET_EXPIRED |
| 2026-06-24 18:45:09 | UNK | 15m | SIG | YES | 0.495 | 0.010 | -8.73 | MARKET_EXPIRED |
| 2026-06-24 19:15:09 | UNK | 15m | SIG | YES | 0.555 | 0.010 | -7.08 | MARKET_EXPIRED |
| 2026-06-24 19:15:26 | UNK | 5m | SIG | YES | 0.595 | 0.010 | -5.85 | MARKET_EXPIRED |
| 2026-06-24 19:30:09 | UNK | 15m | SIG | YES | 0.545 | 0.010 | -12.84 | MARKET_EXPIRED |
| 2026-06-24 19:40:16 | UNK | 5m | SIG | YES | 0.410 | 0.010 | -13.60 | MARKET_EXPIRED |
| 2026-06-24 19:45:10 | UNK | 15m | SIG | YES | 0.515 | 0.010 | -3.03 | MARKET_EXPIRED |
| 2026-06-24 19:50:19 | UNK | 5m | SIG | YES | 0.525 | 0.010 | -10.30 | MARKET_EXPIRED |
| 2026-06-24 21:15:17 | UNK | 15m | SIG | NO | 0.575 | 0.010 | -9.61 | MARKET_EXPIRED |
| 2026-06-24 22:15:09 | UNK | 5m | SIG | NO | 0.525 | 0.010 | -14.42 | MARKET_EXPIRED |
| 2026-06-24 22:45:24 | UNK | 5m | SIG | NO | 0.545 | 0.010 | -14.98 | MARKET_EXPIRED |
| 2026-06-24 23:15:10 | UNK | 15m | SIG | NO | 0.575 | 0.010 | -9.04 | MARKET_EXPIRED |
| 2026-06-24 23:45:33 | UNK | 15m | SIG | NO | 0.505 | 0.010 | -13.37 | MARKET_EXPIRED |
| 2026-06-24 24:30:10 | UNK | 15m | SIG | NO | 0.495 | 0.010 | -6.79 | MARKET_EXPIRED |
| 2026-06-24 25:00:10 | UNK | 15m | SIG | NO | 0.525 | 0.010 | -4.12 | MARKET_EXPIRED |
| 2026-06-25 03:05:11 | UNK | 5m | SIG | YES | 0.495 | 0.010 | -11.15 | MARKET_EXPIRED |
| 2026-06-25 07:15:47 | UNK | 5m | SIG | NO | 0.515 | 0.010 | -11.62 | MARKET_EXPIRED |
| 2026-06-25 07:30:09 | UNK | 5m | SIG | NO | 0.525 | 0.010 | -13.39 | MARKET_EXPIRED |
| 2026-06-25 07:40:09 | UNK | 5m | SIG | NO | 0.505 | 0.010 | -5.44 | MARKET_EXPIRED |
| 2026-06-25 07:45:10 | UNK | 5m | SIG | NO | 0.515 | 0.010 | -11.62 | MARKET_EXPIRED |
| 2026-06-25 08:00:19 | UNK | 15m | SIG | NO | 0.425 | 0.010 | -5.81 | MARKET_EXPIRED |
| 2026-06-25 08:30:09 | UNK | 15m | SIG | NO | 0.535 | 0.010 | -9.45 | MARKET_EXPIRED |
| 2026-06-25 08:50:32 | UNK | 5m | SIG | NO | 0.445 | 0.010 | -10.88 | MARKET_EXPIRED |
| 2026-06-25 09:15:09 | UNK | 15m | SIG | NO | 0.505 | 0.010 | -9.41 | MARKET_EXPIRED |
| 2026-06-25 12:25:29 | UNK | 5m | SIG | YES | 0.405 | 0.010 | -11.46 | MARKET_EXPIRED |
| 2026-06-25 12:30:24 | UNK | 5m | SIG | YES | 0.555 | 0.010 | -9.81 | MARKET_EXPIRED |
| 2026-06-25 12:35:24 | UNK | 5m | SIG | YES | 0.555 | 0.010 | -3.81 | MARKET_EXPIRED |
| 2026-06-25 12:40:24 | UNK | 5m | SIG | YES | 0.535 | 0.010 | -18.38 | MARKET_EXPIRED |
| 2026-06-25 12:40:30 | UNK | 5m | SIG | YES | 0.505 | 0.010 | -16.83 | MARKET_EXPIRED |
| 2026-06-25 12:50:09 | UNK | 5m | SIG | YES | 0.590 | 0.010 | -4.64 | MARKET_EXPIRED |
| 2026-06-25 13:05:23 | UNK | 5m | SIG | YES | 0.515 | 0.010 | -17.17 | MARKET_EXPIRED |
| 2026-06-25 13:05:31 | UNK | 5m | SIG | YES | 0.425 | 0.010 | -19.51 | MARKET_EXPIRED |
| 2026-06-25 13:15:25 | UNK | 15m | SIG | YES | 0.425 | 0.010 | -13.70 | MARKET_EXPIRED |
| 2026-06-25 13:15:31 | UNK | 15m | REV | YES | 0.655 | 0.010 | -13.54 | MARKET_EXPIRED |
| 2026-06-25 13:15:37 | UNK | 15m | REV | YES | 0.455 | 0.010 | -13.79 | MARKET_EXPIRED |
| 2026-06-25 13:15:43 | UNK | 15m | REV | YES | 0.540 | 0.010 | -13.78 | MARKET_EXPIRED |
| 2026-06-25 13:15:48 | UNK | 15m | REV | YES | 0.535 | 0.010 | -13.65 | MARKET_EXPIRED |
| 2026-06-25 13:20:24 | UNK | 5m | SIG | YES | 0.560 | 0.010 | -6.60 | MARKET_EXPIRED |
| 2026-06-25 13:25:22 | UNK | 5m | SIG | YES | 0.540 | 0.010 | -6.89 | MARKET_EXPIRED |
| 2026-06-25 14:00:25 | UNK | 15m | SIG | YES | 0.555 | 0.010 | -9.27 | MARKET_EXPIRED |
| 2026-06-25 14:50:28 | UNK | 5m | SIG | YES | 0.515 | 0.010 | -9.60 | MARKET_EXPIRED |
| 2026-06-25 16:15:09 | UNK | 15m | FV | NO | 0.395 | 0.010 | -6.54 | MARKET_EXPIRED |
| 2026-06-25 16:30:25 | UNK | 15m | SIG | NO | 0.545 | 0.010 | -7.49 | MARKET_EXPIRED |
| 2026-06-25 18:15:33 | UNK | 5m | SIG | NO | 0.575 | 0.010 | -9.61 | MARKET_EXPIRED |
| 2026-06-25 18:45:40 | UNK | 15m | SIG | NO | 0.635 | 0.010 | -5.62 | MARKET_EXPIRED |
| 2026-06-25 21:05:25 | UNK | 5m | SIG | YES | 0.575 | 0.010 | -9.61 | MARKET_EXPIRED |
| 2026-06-25 23:55:09 | UNK | 5m | SIG | NO | 0.585 | 0.010 | -11.50 | MARKET_EXPIRED |
| 2026-06-26 03:20:08 | UNK | 5m | SIG | YES | 0.575 | 0.010 | -7.34 | MARKET_EXPIRED |
| 2026-06-26 03:25:08 | UNK | 5m | SIG | YES | 0.555 | 0.010 | -4.91 | MARKET_EXPIRED |
| 2026-06-26 04:15:10 | UNK | 15m | FV | NO | 0.325 | 0.010 | -11.03 | MARKET_EXPIRED |
| 2026-06-26 05:05:30 | UNK | 5m | FV | NO | 0.655 | 0.010 | -6.45 | MARKET_EXPIRED |
| 2026-06-26 05:55:08 | UNK | 5m | SIG | NO | 0.565 | 0.010 | -13.88 | MARKET_EXPIRED |
| 2026-06-26 07:30:20 | UNK | 15m | SIG | YES | 0.505 | 0.010 | -9.90 | MARKET_EXPIRED |
| 2026-06-26 08:45:34 | UNK | 15m | SIG | NO | 0.600 | 0.010 | -5.90 | MARKET_EXPIRED |
| 2026-06-26 09:35:16 | UNK | 5m | SIG | NO | 0.465 | 0.010 | -10.46 | MARKET_EXPIRED |
| 2026-06-26 10:00:17 | UNK | 15m | SIG | YES | 0.615 | 0.010 | -9.68 | MARKET_EXPIRED |
| 2026-06-26 10:00:23 | UNK | 15m | SIG | YES | 0.555 | 0.010 | -9.81 | MARKET_EXPIRED |
| 2026-06-26 10:00:29 | UNK | 15m | SIG | YES | 0.425 | 0.010 | -9.96 | MARKET_EXPIRED |
| 2026-06-26 10:00:35 | UNK | 15m | SIG | YES | 0.585 | 0.010 | -9.78 | MARKET_EXPIRED |
| 2026-06-26 10:00:40 | UNK | 15m | SIG | YES | 0.590 | 0.010 | -9.86 | MARKET_EXPIRED |
| 2026-06-26 12:00:09 | UNK | 5m | SIG | YES | 0.545 | 0.010 | -13.38 | MARKET_EXPIRED |
| 2026-06-26 12:10:18 | UNK | 5m | SIG | YES | 0.565 | 0.010 | -6.10 | MARKET_EXPIRED |
| 2026-06-26 12:25:08 | UNK | 5m | SIG | YES | 0.495 | 0.010 | -7.27 | MARKET_EXPIRED |
| 2026-06-26 12:30:09 | UNK | 15m | SIG | YES | 0.545 | 0.010 | -9.10 | MARKET_EXPIRED |
| 2026-06-26 12:30:17 | UNK | 15m | SIG | YES | 0.505 | 0.010 | -9.41 | MARKET_EXPIRED |
| 2026-06-26 12:40:50 | UNK | 5m | FV | NO | 0.335 | 0.010 | -18.52 | MARKET_EXPIRED |
| 2026-06-26 12:45:09 | UNK | 15m | SIG | YES | 0.505 | 0.010 | -5.94 | MARKET_EXPIRED |
| 2026-06-26 12:45:16 | UNK | 5m | SIG | YES | 0.545 | 0.010 | -8.56 | MARKET_EXPIRED |
| 2026-06-26 13:15:09 | UNK | 15m | SIG | YES | 0.505 | 0.010 | -13.37 | MARKET_EXPIRED |
| 2026-06-26 13:45:09 | UNK | 15m | SIG | YES | 0.425 | 0.010 | -9.13 | MARKET_EXPIRED |
| 2026-06-26 16:00:31 | UNK | 15m | SIG | YES | 0.600 | 0.010 | -3.54 | MARKET_EXPIRED |
| 2026-06-26 16:25:22 | UNK | 5m | SIG | NO | 0.485 | 0.010 | -18.05 | MARKET_EXPIRED |

## Detailed Analysis Per Trade



### Loss #134: UNK 5m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 03:20:08 (Hour: 03 SAST, UTC: 01:20:08)
- **Exit Time (SAST):** 2026-06-26 01:25:09
- **Entry Price:** 0.575 | **Exit Price:** 0.010 | **PnL:** $-7.34 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 25, 9:20PM-9:25PM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  03:20:08 [DEBUG] zisi.whale_tracker: [WhaleTracker] BTC fetched 50 trades
  03:20:08 [INFO ] zisi.whale_tracker: [WhaleTracker] BTC → pressure=-0.985 dir=bearish whales=17 buy_vol=1366 sell_vol=180670 multiplier=0.850
  03:20:08 [INFO ] zisi.edge_orchestrator: [EDGE] BTC UP | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=0.30 whale=0.75 sentiment=1.03 → boost=-0.153
  03:20:08 [INFO ] zisi.engine: [EDGE] BTC/5m Score adjusted by boost: 0.78 -> 0.63 (boost=-0.15)
  03:20:08 [INFO ] zisi.confluence_engine: [Confluence] BTC UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=59.88, Mom=-0.09%) | 5m=NEUTRAL(RSI=20.31, Mom=0.05%) | 15m=DOWN(RSI=29.03, Mom=-0.29%) | 1h=DOWN(RSI=37.5, Mom=-1.01%)
  03:20:08 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=2/4 (MODERATE) boost=0.05 | 1m=NEUTRAL(RSI=59.88, Mom=-0.09%) | 5m=NEUTRAL(RSI=20.31, Mom=0.05%) | 15m=DOWN(RSI=29.03, Mom=-0.29%) | 1h=DOWN(RSI=37.5, Mom=-1.01%)
  03:20:08 [INFO ] zisi.engine: [ENGINE] BTC/5m SIGNAL: UP | Score=0.63 | up=0.5750 dn=0.4250 | dual=False | Bitcoin Up or Down - June 25, 9:20PM-9:25PM ET
  03:20:08 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7647, fraction=0.1912)
  03:20:08 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.74 kelly_fraction=0.1912 | regime*1.20 anti*0.30 heat*1.00 whale*0.75 | -> $15.14 | cycle=$15.14/1 trades
  03:20:08 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 0.80x -> $12.11
  03:20:08 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $12.07 (shares=21, conf=0.63, asset_w=1.00)
  03:20:08 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  03:20:08 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $12.07 → $7.24
  03:20:08 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  03:20:08 [INFO ] zisi.trader: [PAPER] BUY YES | 13 shares @ 0.5750 = $7.4750 | [UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 25,
  03:20:08 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 25, 9:20PM-9:25PM ET' (entry=0.5750) -> target 0.7200, stop -1.0
  03:20:08 [INFO ] zisi.main: [TRADE OPENED] BTC/5m UP | $7.47 @ 0.5750 | score=0.63 | SINGLE
  03:20:08 [INFO ] zisi.logger: [SIGNAL-EVAL] BTC | score=0.63 | type=REAL | conf=0.63
  03:20:09 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7561, fraction=0.1890)
  03:20:09 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.69 kelly_fraction=0.1890 | regime*1.20 anti*0.30 heat*1.00 whale*1.00 | -> $29.00 | cycle=$29.00/1 trades
  03:20:09 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 0.80x -> $23.20
  ```

---



### Loss #135: UNK 5m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 03:25:08 (Hour: 03 SAST, UTC: 01:25:08)
- **Exit Time (SAST):** 2026-06-26 01:30:08
- **Entry Price:** 0.555 | **Exit Price:** 0.010 | **PnL:** $-4.91 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][DOGE][5m][SINGLE] Dogecoin Up or Down - June 25, 9:25PM-9:30PM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  03:25:08 [INFO ] zisi.edge_orchestrator: [EDGE] XRP UP | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=0.30 whale=1.10 sentiment=1.00 → boost=-0.050
  03:25:08 [INFO ] zisi.engine: [EDGE] XRP/5m Score adjusted by boost: 0.98 -> 0.93 (boost=-0.05)
  03:25:08 [INFO ] zisi.confluence_engine: [Confluence] XRP UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=DOWN(RSI=19.48, Mom=-0.17%) | 5m=DOWN(RSI=10.85, Mom=-0.33%) | 15m=DOWN(RSI=34.47, Mom=-0.83%) | 1h=DOWN(RSI=36.49, Mom=-0.87%)
  03:25:08 [INFO ] zisi.confluence_engine: [Confluence] XRP DOWN: score=4/4 (MAXIMUM) boost=0.15 | 1m=DOWN(RSI=19.48, Mom=-0.17%) | 5m=DOWN(RSI=10.85, Mom=-0.33%) | 15m=DOWN(RSI=34.47, Mom=-0.83%) | 1h=DOWN(RSI=36.49, Mom=-0.87%)
  03:25:08 [WARNING] zisi.engine: [TREND-FREEZE] XRP midpoint entry frozen. Alignment=4/4, ADX=82.5. Bypassing entry to avoid drawdown.
  03:25:08 [INFO ] zisi.main: [MAIN] XRP/5m: No L2 book/signal at 8.8s — retrying...
  03:25:08 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  03:25:08 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7753, fraction=0.1938)
  03:25:08 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.80 kelly_fraction=0.1938 | regime*1.20 anti*0.30 heat*1.00 whale*1.00 | -> $31.40 | cycle=$31.40/1 trades
  03:25:08 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 0.80x -> $25.12
  03:25:08 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $24.98 (shares=45, conf=0.83, asset_w=1.00)
  03:25:08 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  03:25:08 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $24.98 → $14.98
  03:25:08 [INFO ] zisi.main: [RISK] Altcoin DOGE Sizing calibrated to 35% (max $35): $5.24
  03:25:08 [INFO ] zisi.trader: [PAPER] BUY YES | 9 shares @ 0.5550 = $4.9950 | [UPDOWN][DOGE][5m][SINGLE] Dogecoin Up or Down - June 2
  03:25:08 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][DOGE][5m][SINGLE] Dogecoin Up or Down - June 25, 9:25PM-9:30PM ET' (entry=0.5550) -> target 0.7200, stop -1.0
  03:25:08 [INFO ] zisi.main: [TRADE OPENED] DOGE/5m UP | $5.00 @ 0.5550 | score=0.83 | SINGLE
  03:25:09 [INFO ] zisi.logger: [SIGNAL-EVAL] DOGE | score=0.83 | type=REAL | conf=0.83
  03:25:09 [INFO ] zisi.trader: [REAL-RESOLVE] BTC 5m/zisi_2de: candle 59592.2400→59484.0100 (DN) | pos=YES → 0.01
  03:25:09 [INFO ] zisi.trader: [REAL-RESOLVE] zisi_2de284e2b4a8: Binance candle → LOSS @ 0.01
  03:25:09 [INFO ] zisi.trader: [TRADE CLOSED] BTC/5m UP | LOSS | entry=57¢ exit=1¢ | pnl=-7.34$ (-98.2%) | MARKET_EXPIRED | held=5m
  ```

---



### Loss #136: UNK 15m FV (NO)
- **Entry Time (SAST):** 2026-06-26 04:15:10 (Hour: 04 SAST, UTC: 02:15:10)
- **Exit Time (SAST):** 2026-06-26 02:30:14
- **Entry Price:** 0.325 | **Exit Price:** 0.010 | **PnL:** $-11.03 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][ETH][15m][FAIR_VAL] Ethereum Up or Down - June 25, 10:15PM-10:30PM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  04:15:10 [INFO ] zisi.whale_tracker: [WhaleTracker] ETH → pressure=1.000 dir=bullish whales=4 buy_vol=1082 sell_vol=0 multiplier=1.100
  04:15:10 [INFO ] zisi.edge_orchestrator: [EDGE] ETH DOWN | regime=TRENDING(×1.20) confluence=4(+0.15) heat=1.00 anti=0.30 whale=0.75 sentiment=1.00 → boost=0.070
  04:15:10 [INFO ] zisi.engine: [EDGE] ETH/15m Score adjusted by boost: 0.85 -> 0.92 (boost=+0.07)
  04:15:10 [INFO ] zisi.engine: [ENGINE] ETH/15m SIGNAL: DOWN | Score=0.92 | up=0.6750 dn=0.3250 | dual=False | Ethereum Up or Down - June 25, 10:15PM-10:30PM ET
  04:15:10 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.8519, fraction=0.2130)
  04:15:10 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=2.08 kelly_fraction=0.2130 | regime*1.20 anti*0.30 heat*1.00 whale*0.75 | -> $25.83 | cycle=$25.83/1 trades
  04:15:10 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 0.80x -> $20.66
  04:15:10 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $20.80 (shares=64, conf=0.76, asset_w=1.00)
  04:15:10 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  04:15:10 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $27.04 → $16.22
  04:15:10 [INFO ] zisi.main: [RISK] ETH/15m corroboration_mult=1.3 → bet $16.22
  04:15:10 [INFO ] zisi.main: [RISK] 15m size discount -30%: $11.36
  04:15:10 [DEBUG] zisi.confluence_engine: [Confluence] fetched 30 closes for BTCUSDT/1h
  04:15:10 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=4/4 (MAXIMUM) boost=0.15 | 1m=DOWN(RSI=15.18, Mom=-0.79%) | 5m=DOWN(RSI=21.34, Mom=-1.14%) | 15m=DOWN(RSI=25.18, Mom=-0.93%) | 1h=DOWN(RSI=33.44, Mom=-1.85%)
  04:15:10 [INFO ] zisi.trader: [PAPER] BUY NO | 35 shares @ 0.3250 = $11.3750 | [UPDOWN][ETH][15m][FAIR_VAL] Ethereum Up or Down - June
  04:15:10 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][ETH][15m][FAIR_VAL] Ethereum Up or Down - June 25, 10:15PM-10:30PM ET' (entry=0.3250) -> target 0.8800, stop -1.0
  04:15:10 [INFO ] zisi.main: [TRADE OPENED] ETH/15m DOWN | $11.38 @ 0.3250 | score=0.92 | FAIR_VAL
  04:15:10 [DEBUG] zisi.volatility_surface: [VolSurface] SOL OI = 10421010.89
  04:15:10 [INFO ] zisi.volatility_surface: [VolSurface] SOL → bias=neutral strength=0.000 oi=weak_rally sentiment=-0.100 modifier=1.000
  04:15:11 [DEBUG] zisi.volatility_surface: [VolSurface] BTC funding rate = 0.000053
  04:15:11 [DEBUG] zisi.whale_tracker: [WhaleTracker] SOL fetched 50 trades
  ```

---



### Loss #137: UNK 5m FV (NO)
- **Entry Time (SAST):** 2026-06-26 05:05:30 (Hour: 05 SAST, UTC: 03:05:30)
- **Exit Time (SAST):** 2026-06-26 03:10:13
- **Entry Price:** 0.655 | **Exit Price:** 0.010 | **PnL:** $-6.45 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][XRP][5m][FAIR_VAL] XRP Up or Down - June 25, 11:05PM-11:10PM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  05:05:29 [INFO ] zisi.engine: [EDGE] XRP/5m Score adjusted by boost: 0.67 -> 0.77 (boost=+0.10)
  05:05:29 [INFO ] zisi.engine: [ENGINE] XRP/5m SIGNAL: DOWN | Score=0.77 | up=0.3450 dn=0.6550 | dual=False | XRP Up or Down - June 25, 11:05PM-11:10PM ET
  05:05:29 [INFO ] zisi.main: [LEADER-PROP] XRP/5m DOWN: BOTH leaders (BTC & ETH) confirm — propagating conviction (corr×1.3)
  05:05:29 [INFO ] zisi.regime_detector: [RegimeDetector] initialised — timeframe=5m ATR window=14 lookback=50 BB(20, 2.0)
  05:05:29 [DEBUG] zisi.regime_detector: [Regime] BTC bulk update (30) → regime=VOLATILE_CHAOS ATR=0.2529% Kelly×0.30
  05:05:30 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7101, fraction=0.1775)
  05:05:30 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.53 kelly_fraction=0.1775 | regime*1.20 anti*0.30 heat*1.00 whale*1.10 | -> $25.08 | cycle=$25.08/1 trades
  05:05:30 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 0.80x -> $20.06
  05:05:30 [INFO ] zisi.engine: [SIZE] Price 0.6550 in 70c zone -> x0.70 scaling
  05:05:30 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $13.76 (shares=21, conf=0.75, asset_w=1.00)
  05:05:30 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  05:05:30 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $17.88 → $10.73
  05:05:30 [INFO ] zisi.main: [RISK] XRP/5m corroboration_mult=1.3 → bet $10.73
  05:05:30 [INFO ] zisi.main: [RISK] SOL/XRP Sizing calibrated to 60%: $6.44
  05:05:30 [INFO ] zisi.trader: [PAPER] BUY NO | 10 shares @ 0.6550 = $6.5500 | [UPDOWN][XRP][5m][FAIR_VAL] XRP Up or Down - June 25, 1
  05:05:30 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][XRP][5m][FAIR_VAL] XRP Up or Down - June 25, 11:05PM-11:10PM ET' (entry=0.6550) -> target 0.7200, stop -1.0
  05:05:30 [INFO ] zisi.main: [TRADE OPENED] XRP/5m DOWN | $6.55 @ 0.6550 | score=0.77 | FAIR_VAL
  05:05:30 [INFO ] zisi.logger: [SIGNAL-EVAL] XRP | score=0.77 | type=REAL | conf=0.77
  05:05:30 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  05:05:33 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  05:05:34 [DEBUG] zisi.balance_history: [EQUITY] Snapshot: $595.68 | P&L: $+545.68 | trades: 972
  ```

---



### Loss #138: UNK 5m SIG (NO)
- **Entry Time (SAST):** 2026-06-26 05:55:08 (Hour: 05 SAST, UTC: 03:55:08)
- **Exit Time (SAST):** 2026-06-26 04:00:25
- **Entry Price:** 0.565 | **Exit Price:** 0.010 | **PnL:** $-13.88 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 25, 11:55PM-12:00AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  05:55:08 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  05:55:08 [DEBUG] zisi.whale_tracker: [WhaleTracker] BTC fetched 50 trades
  05:55:08 [INFO ] zisi.whale_tracker: [WhaleTracker] BTC → pressure=-0.293 dir=neutral whales=13 buy_vol=1906 sell_vol=3490 multiplier=1.000
  05:55:08 [INFO ] zisi.edge_orchestrator: [EDGE] BTC DOWN | regime=MEAN_REVERTING(×1.20) confluence=0(+-0.10) heat=1.00 anti=0.30 whale=1.00 sentiment=1.00 → boost=-0.100
  05:55:08 [INFO ] zisi.engine: [EDGE] BTC/5m Score adjusted by boost: 0.90 -> 0.80 (boost=-0.10)
  05:55:08 [INFO ] zisi.confluence_engine: [Confluence] BTC UP: score=1/4 (WEAK) boost=0.00 | 1m=NEUTRAL(RSI=67.59, Mom=0.08%) | 5m=UP(RSI=85.07, Mom=0.52%) | 15m=NEUTRAL(RSI=50.13, Mom=2.08%) | 1h=NEUTRAL(RSI=62.43, Mom=-0.02%)
  05:55:08 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=67.59, Mom=0.08%) | 5m=UP(RSI=85.07, Mom=0.52%) | 15m=NEUTRAL(RSI=50.13, Mom=2.08%) | 1h=NEUTRAL(RSI=62.43, Mom=-0.02%)
  05:55:08 [INFO ] zisi.engine: [ENGINE] BTC/5m SIGNAL: DOWN | Score=0.80 | up=0.4350 dn=0.5650 | dual=False | Bitcoin Up or Down - June 25, 11:55PM-12:00AM ET
  05:55:08 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7701, fraction=0.1925)
  05:55:08 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.77 kelly_fraction=0.1925 | regime*1.20 anti*0.30 heat*1.00 whale*1.00 | -> $29.00 | cycle=$29.00/1 trades
  05:55:08 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 0.80x -> $23.20
  05:55:08 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $23.16 (shares=41, conf=0.80, asset_w=1.00)
  05:55:08 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  05:55:08 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $23.16 → $13.90
  05:55:08 [INFO ] zisi.trader: [PAPER] BUY NO | 25 shares @ 0.5650 = $14.1250 | [UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 25,
  05:55:08 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 25, 11:55PM-12:00AM ET' (entry=0.5650) -> target 0.7200, stop -1.0
  05:55:08 [DEBUG] zisi.trader: [MEMORY] Pruned 5 stale CLOSED positions from memory
  05:55:08 [INFO ] zisi.main: [TRADE OPENED] BTC/5m DOWN | $14.12 @ 0.5650 | score=0.80 | SINGLE
  05:55:08 [INFO ] zisi.logger: [SIGNAL-EVAL] BTC | score=0.80 | type=REAL | conf=0.80
  05:55:09 [INFO ] zisi.main: [CORR-MAGNITUDE] BTC/5m lead DOWN move -0.0487% = 0.23x window range (need aligned and >= 0.40x) — no shadows this window
  05:55:09 [DEBUG] zisi.arbitrage: [ARB] TCP connections warmed successfully.
  ```

---



### Loss #139: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 07:30:20 (Hour: 07 SAST, UTC: 05:30:20)
- **Exit Time (SAST):** 2026-06-26 05:45:10
- **Entry Price:** 0.505 | **Exit Price:** 0.010 | **PnL:** $-9.90 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][ETH][15m][SINGLE] Ethereum Up or Down - June 26, 1:30AM-1:45AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  07:30:20 [INFO ] zisi.engine: [EDGE] ETH/15m Score adjusted by boost: 0.92 -> 1.00 (boost=+0.13)
  07:30:20 [INFO ] zisi.confluence_engine: [Confluence] ETH UP: score=2/4 (MODERATE) boost=0.05 | 1m=UP(RSI=60.55, Mom=0.13%) | 5m=NEUTRAL(RSI=59.45, Mom=0.28%) | 15m=UP(RSI=72.53, Mom=0.32%) | 1h=NEUTRAL(RSI=46.14, Mom=-0.17%)
  07:30:20 [INFO ] zisi.confluence_engine: [Confluence] ETH DOWN: score=0/4 (CONFLICT) boost=-0.10 | 1m=UP(RSI=60.55, Mom=0.13%) | 5m=NEUTRAL(RSI=59.45, Mom=0.28%) | 15m=UP(RSI=72.53, Mom=0.32%) | 1h=NEUTRAL(RSI=46.14, Mom=-0.17%)
  07:30:20 [INFO ] zisi.engine: [ENGINE] ETH/15m SIGNAL: UP | Score=1.00 | up=0.5050 dn=0.4950 | dual=False | Ethereum Up or Down - June 26, 1:30AM-1:45AM ET
  07:30:20 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7980, fraction=0.1995)
  07:30:20 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.98 kelly_fraction=0.1995 | regime*1.10 anti*0.40 heat*1.00 whale*1.10 | -> $40.00 | cycle=$40.00/1 trades
  07:30:20 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 0.80x -> $32.00
  07:30:20 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $31.82 (shares=63, conf=1.00, asset_w=1.00)
  07:30:20 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  07:30:20 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $31.82 → $19.09
  07:30:20 [INFO ] zisi.main: [RISK] 15m size discount -30%: $13.36
  07:30:20 [INFO ] zisi.main: [RISK] SIGNAL trade size capped at $10.0: $13.36 -> $10.00
  07:30:20 [DEBUG] zisi.whale_tracker: [WhaleTracker] ETH fetched 50 trades
  07:30:20 [INFO ] zisi.whale_tracker: [WhaleTracker] ETH → pressure=1.000 dir=bullish whales=2 buy_vol=189 sell_vol=0 multiplier=1.100
  07:30:20 [INFO ] zisi.trader: [PAPER] BUY YES | 20 shares @ 0.5050 = $10.1000 | [UPDOWN][ETH][15m][SINGLE] Ethereum Up or Down - June 2
  07:30:20 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][ETH][15m][SINGLE] Ethereum Up or Down - June 26, 1:30AM-1:45AM ET' (entry=0.5050) -> target 0.8800, stop -1.0
  07:30:20 [INFO ] zisi.main: [TRADE OPENED] ETH/15m UP | $10.10 @ 0.5050 | score=1.00 | SINGLE
  07:30:20 [INFO ] zisi.edge_orchestrator: [EDGE] ETH UP | regime=COMPRESSION(×1.10) confluence=2(+0.05) heat=1.00 anti=0.40 whale=1.10 sentiment=1.03 → boost=0.127
  07:30:20 [INFO ] zisi.engine: [EDGE] ETH/5m Score adjusted by boost: 0.82 -> 0.95 (boost=+0.13)
  07:30:20 [INFO ] zisi.confluence_engine: [Confluence] ETH UP: score=2/4 (MODERATE) boost=0.05 | 1m=UP(RSI=60.55, Mom=0.13%) | 5m=NEUTRAL(RSI=59.45, Mom=0.28%) | 15m=UP(RSI=72.53, Mom=0.32%) | 1h=NEUTRAL(RSI=46.14, Mom=-0.17%)
  07:30:20 [INFO ] zisi.confluence_engine: [Confluence] ETH DOWN: score=0/4 (CONFLICT) boost=-0.10 | 1m=UP(RSI=60.55, Mom=0.13%) | 5m=NEUTRAL(RSI=59.45, Mom=0.28%) | 15m=UP(RSI=72.53, Mom=0.32%) | 1h=NEUTRAL(RSI=46.14, Mom=-0.17%)
  ```

---



### Loss #140: UNK 15m SIG (NO)
- **Entry Time (SAST):** 2026-06-26 08:45:34 (Hour: 08 SAST, UTC: 06:45:34)
- **Exit Time (SAST):** 2026-06-26 07:00:03
- **Entry Price:** 0.600 | **Exit Price:** 0.010 | **PnL:** $-5.90 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][XRP][15m][SINGLE] XRP Up or Down - June 26, 2:45AM-3:00AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  08:45:34 [INFO ] zisi.main: [MAIN] ETH/5m SKIP (no_signal)
  08:45:34 [INFO ] zisi.main: [MAIN] SOL/5m: Signal evaluation retry window closed (elapsed=34.1s > 30.0s) — skip
  08:45:34 [DEBUG] zisi.metrics: Skip recorded — no_signal:
  08:45:34 [INFO ] zisi.main: [MAIN] SOL/5m SKIP (no_signal)
  08:45:34 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7500, fraction=0.1875)
  08:45:34 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.67 kelly_fraction=0.1875 | regime*1.10 anti*0.40 heat*1.00 whale*1.10 | -> $30.60 | cycle=$30.60/1 trades
  08:45:34 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 0.80x -> $24.48
  08:45:34 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $24.60 (shares=41, conf=0.82, asset_w=1.00)
  08:45:34 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  08:45:34 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $31.98 → $19.19
  08:45:34 [INFO ] zisi.main: [RISK] XRP/15m corroboration_mult=1.3 → bet $19.19
  08:45:34 [INFO ] zisi.main: [RISK] 15m size discount -30%: $13.43
  08:45:34 [INFO ] zisi.main: [RISK] SIGNAL trade size capped at $10.0: $13.43 -> $10.00
  08:45:34 [INFO ] zisi.main: [RISK] SOL/XRP Sizing calibrated to 60%: $6.00
  08:45:34 [INFO ] zisi.trader: [PAPER] BUY NO | 10 shares @ 0.6000 = $6.0000 | [UPDOWN][XRP][15m][SINGLE] XRP Up or Down - June 26, 2:
  08:45:34 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][XRP][15m][SINGLE] XRP Up or Down - June 26, 2:45AM-3:00AM ET' (entry=0.6000) -> target 0.8800, stop -1.0
  08:45:34 [INFO ] zisi.main: [TRADE OPENED] XRP/15m DOWN | $6.00 @ 0.6000 | score=0.82 | SINGLE
  08:45:34 [INFO ] zisi.main: [MAIN] SOL/15m: Signal evaluation retry window closed (elapsed=34.2s > 30.0s) — skip
  08:45:34 [DEBUG] zisi.metrics: Skip recorded — no_signal:
  08:45:34 [INFO ] zisi.main: [MAIN] SOL/15m SKIP (no_signal)
  08:45:34 [INFO ] zisi.main: [MAIN] BTC/5m: Signal evaluation retry window closed (elapsed=34.3s > 30.0s) — skip
  ```

---



### Loss #141: UNK 5m SIG (NO)
- **Entry Time (SAST):** 2026-06-26 09:35:16 (Hour: 09 SAST, UTC: 07:35:16)
- **Exit Time (SAST):** 2026-06-26 07:40:05
- **Entry Price:** 0.465 | **Exit Price:** 0.010 | **PnL:** $-10.46 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][ETH][5m][SINGLE] Ethereum Up or Down - June 26, 3:35AM-3:40AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  09:35:16 [INFO ] zisi.engine: [ENGINE] SOL/5m SIGNAL: DOWN | Score=0.86 | up=0.5250 dn=0.4750 | dual=False | Solana Up or Down - June 26, 3:35AM-3:40AM ET
  09:35:16 [DEBUG] zisi.whale_tracker: [WhaleTracker] ETH fetched 50 trades
  09:35:16 [INFO ] zisi.whale_tracker: [WhaleTracker] ETH → pressure=0.928 dir=bullish whales=9 buy_vol=18831 sell_vol=702 multiplier=1.100
  09:35:16 [INFO ] zisi.edge_orchestrator: [EDGE] ETH DOWN | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=0.50 whale=0.75 sentiment=1.00 → boost=-0.180
  09:35:16 [INFO ] zisi.engine: [EDGE] ETH/5m Score adjusted by boost: 0.90 -> 0.72 (boost=-0.18)
  09:35:16 [INFO ] zisi.confluence_engine: [Confluence] ETH UP: score=2/4 (MODERATE) boost=0.05 | 1m=NEUTRAL(RSI=59.27, Mom=-0.07%) | 5m=UP(RSI=83.1, Mom=0.17%) | 15m=UP(RSI=70.9, Mom=0.55%) | 1h=NEUTRAL(RSI=51.87, Mom=1.49%)
  09:35:16 [INFO ] zisi.confluence_engine: [Confluence] ETH DOWN: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=59.27, Mom=-0.07%) | 5m=UP(RSI=83.1, Mom=0.17%) | 15m=UP(RSI=70.9, Mom=0.55%) | 1h=NEUTRAL(RSI=51.87, Mom=1.49%)
  09:35:16 [INFO ] zisi.engine: [ENGINE] ETH/5m SIGNAL: DOWN | Score=0.72 | up=0.5350 dn=0.4650 | dual=False | Ethereum Up or Down - June 26, 3:35AM-3:40AM ET
  09:35:16 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.8131, fraction=0.2033)
  09:35:16 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=1.15 kelly_fraction=0.2033 | regime*1.20 anti*0.50 heat*1.00 whale*0.75 | -> $22.60 | cycle=$22.60/1 trades
  09:35:16 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 0.80x -> $18.08
  09:35:16 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $18.14 (shares=39, conf=0.72, asset_w=1.00)
  09:35:16 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  09:35:16 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $18.14 → $10.88
  09:35:16 [INFO ] zisi.trader: [PAPER] BUY NO | 23 shares @ 0.4650 = $10.6950 | [UPDOWN][ETH][5m][SINGLE] Ethereum Up or Down - June 26
  09:35:16 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][ETH][5m][SINGLE] Ethereum Up or Down - June 26, 3:35AM-3:40AM ET' (entry=0.4650) -> target 0.7200, stop -1.0
  09:35:16 [INFO ] zisi.main: [TRADE OPENED] ETH/5m DOWN | $10.70 @ 0.4650 | score=0.72 | SINGLE
  09:35:16 [INFO ] zisi.logger: [SIGNAL-EVAL] ETH | score=0.72 | type=REAL | conf=0.72
  09:35:17 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.8095, fraction=0.2024)
  09:35:17 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=1.11 kelly_fraction=0.2024 | regime*1.20 anti*0.50 heat*1.00 whale*1.10 | -> $33.54 | cycle=$33.54/1 trades
  09:35:17 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 0.80x -> $26.83
  ```

---



### Loss #142: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 10:00:17 (Hour: 10 SAST, UTC: 08:00:17)
- **Exit Time (SAST):** 2026-06-26 08:15:14
- **Entry Price:** 0.615 | **Exit Price:** 0.010 | **PnL:** $-9.68 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26, 4:00AM-4:15AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  10:00:17 [INFO ] zisi.main: [MAIN] SOL/5m: No L2 book/signal at 17.3s — retrying...
  10:00:17 [DEBUG] zisi.whale_tracker: [WhaleTracker] BTC fetched 50 trades
  10:00:17 [INFO ] zisi.whale_tracker: [WhaleTracker] BTC → pressure=1.000 dir=bullish whales=3 buy_vol=1331 sell_vol=0 multiplier=1.100
  10:00:17 [INFO ] zisi.edge_orchestrator: [EDGE] BTC UP | regime=TRENDING(×1.20) confluence=1(+0.00) heat=1.00 anti=0.60 whale=1.10 sentiment=1.03 → boost=0.077
  10:00:17 [INFO ] zisi.engine: [EDGE] BTC/15m Score adjusted by boost: 0.75 -> 0.83 (boost=+0.08)
  10:00:17 [INFO ] zisi.engine: [ENGINE] BTC/15m SIGNAL: UP | Score=0.83 | up=0.6150 dn=0.3850 | dual=False | Bitcoin Up or Down - June 26, 4:00AM-4:15AM ET
  10:00:17 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7403, fraction=0.1851)
  10:00:17 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.63 kelly_fraction=0.1851 | regime*1.20 anti*0.60 heat*1.00 whale*1.10 | -> $31.47 | cycle=$31.47/1 trades
  10:00:17 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $31.47
  10:00:17 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $31.36 (shares=51, conf=0.83, asset_w=1.00)
  10:00:17 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  10:00:17 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $31.36 → $18.82
  10:00:17 [INFO ] zisi.main: [RISK] 15m size discount -30%: $13.17
  10:00:17 [INFO ] zisi.main: [RISK] SIGNAL trade size capped at $10.0: $13.17 -> $10.00
  10:00:17 [INFO ] zisi.trader: [PAPER] BUY YES | 16 shares @ 0.6150 = $9.8400 | [UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26
  10:00:17 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26, 4:00AM-4:15AM ET' (entry=0.6150) -> target 0.8800, stop -1.0
  10:00:17 [DEBUG] zisi.trader: [MEMORY] Pruned 1 stale CLOSED positions from memory
  10:00:17 [INFO ] zisi.main: [TRADE OPENED] BTC/15m UP | $9.84 @ 0.6150 | score=0.83 | SINGLE
  10:00:17 [INFO ] zisi.logger: [SIGNAL-EVAL] BTC | score=0.83 | type=REAL | conf=0.83
  10:00:17 [INFO ] zisi.engine: [FAIR-VALUE] XRP/15m UP | fp=0.767 quote=0.615 edge=0.152 (moderate)
  10:00:17 [INFO ] zisi.confluence_engine: [Confluence] XRP UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=55.17, Mom=-0.01%) | 5m=NEUTRAL(RSI=67.9, Mom=0.05%) | 15m=NEUTRAL(RSI=81.27, Mom=0.07%) | 1h=NEUTRAL(RSI=58.25, Mom=2.12%)
  ```

---



### Loss #143: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 10:00:23 (Hour: 10 SAST, UTC: 08:00:23)
- **Exit Time (SAST):** 2026-06-26 08:15:15
- **Entry Price:** 0.555 | **Exit Price:** 0.010 | **PnL:** $-9.81 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][ETH][15m][SIGNAL] Ethereum Up or Down - June 26, 4:00AM-4:15AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  10:00:18 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $28.26
  10:00:18 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $28.29 (shares=46, conf=0.79, asset_w=1.00)
  10:00:18 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  10:00:18 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $36.78 → $22.07
  10:00:18 [INFO ] zisi.main: [RISK] XRP/15m corroboration_mult=1.3 → bet $22.07
  10:00:18 [INFO ] zisi.main: [RISK] 15m size discount -30%: $15.45
  10:00:18 [INFO ] zisi.main: [RISK] SOL/XRP Sizing calibrated to 60%: $9.27
  10:00:18 [INFO ] zisi.main: [MAIN] XRP/15m COOLDOWN skip — next entry in 1.6s
  10:00:18 [INFO ] zisi.logger: [SIGNAL-EVAL] XRP | score=0.65 | type=MISSED | conf=0.65
  10:00:19 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  10:00:19 [INFO ] zisi.regime_detector: [RegimeDetector] initialised — timeframe=5m ATR window=14 lookback=50 BB(20, 2.0)
  10:00:19 [DEBUG] zisi.regime_detector: [Regime] BTC bulk update (30) → regime=MEAN_REVERTING ATR=0.1040% Kelly×1.00
  10:00:22 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  10:00:23 [INFO ] zisi.engine: [ENGINE] ETH/15m: [PRE-FETCH HIT] eth-updown-15m-1782460800 up=0.5550 dn=0.4450 spread=0.0200
  10:00:23 [INFO ] zisi.trader: [PAPER] BUY YES | 18 shares @ 0.5550 = $9.9900 | [UPDOWN][ETH][15m][SIGNAL] Ethereum Up or Down - June 2
  10:00:23 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][ETH][15m][SIGNAL] Ethereum Up or Down - June 26, 4:00AM-4:15AM ET' (entry=0.5550) -> target 0.8800, stop -1.0
  10:00:23 [INFO ] zisi.main: [TRADE OPENED] ETH/15m UP | $9.99 @ 0.5550 | score=0.83 | SIGNAL
  10:00:23 [INFO ] zisi.main: [CORR] ETH/15m UP | $10.00 @ 0.5550 | shadow of BTC/15m [SIG] → logged as SIGNAL
  10:00:24 [INFO ] zisi.engine: [ENGINE] DOGE/15m: [PRE-FETCH HIT] doge-updown-15m-1782460800 up=0.5500 dn=0.4500 spread=0.2000
  10:00:24 [INFO ] zisi.engine: [ENGINE] ETH/5m: [PRE-FETCH HIT] eth-updown-5m-1782460800 up=0.6350 dn=0.3650 spread=0.0200
  10:00:24 [INFO ] zisi.engine: [PRICE-SOURCE] ETH/5m: Using authoritative Chainlink price (Spot=1581.9800, Strike=1580.6800)
  ```

---



### Loss #144: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 10:00:29 (Hour: 10 SAST, UTC: 08:00:29)
- **Exit Time (SAST):** 2026-06-26 08:15:15
- **Entry Price:** 0.425 | **Exit Price:** 0.010 | **PnL:** $-9.96 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][SOL][15m][SIGNAL] Solana Up or Down - June 26, 4:00AM-4:15AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  10:00:25 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=46.92, Mom=-0.07%) | 5m=NEUTRAL(RSI=65.38, Mom=-0.04%) | 15m=NEUTRAL(RSI=68.43, Mom=0.09%) | 1h=UP(RSI=60.61, Mom=1.08%)
  10:00:25 [INFO ] zisi.engine: [ENGINE] BTC/5m: RSI=65.31 Mom=-0.0429 -> NEUTRAL (dual-only path).
  10:00:25 [INFO ] zisi.main: [MAIN] BTC/5m: No L2 book/signal at 25.2s — retrying...
  10:00:25 [DEBUG] zisi.confluence_engine: [Confluence] fetched 30 closes for SOLUSDT/1m
  10:00:25 [INFO ] zisi.confluence_engine: [Confluence] SOL UP: score=3/4 (STRONG) boost=0.10 | 1m=NEUTRAL(RSI=54.55, Mom=0.08%) | 5m=UP(RSI=75.36, Mom=0.24%) | 15m=UP(RSI=86.38, Mom=0.30%) | 1h=UP(RSI=78.02, Mom=4.06%)
  10:00:25 [INFO ] zisi.confluence_engine: [Confluence] SOL DOWN: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=54.55, Mom=0.08%) | 5m=UP(RSI=75.36, Mom=0.24%) | 15m=UP(RSI=86.38, Mom=0.30%) | 1h=UP(RSI=78.02, Mom=4.06%)
  10:00:25 [INFO ] zisi.engine: [ENGINE] SOL/5m: Spot OFI divergence — blocking entry.
  10:00:25 [INFO ] zisi.main: [MAIN] SOL/5m: No L2 book/signal at 25.4s — retrying...
  10:00:25 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  10:00:26 [DEBUG] zisi.arbitrage: [ARB] TCP connections warmed successfully.
  10:00:27 [INFO ] zisi.regime_detector: [RegimeDetector] initialised — timeframe=5m ATR window=14 lookback=50 BB(20, 2.0)
  10:00:27 [DEBUG] zisi.regime_detector: [Regime] BTC bulk update (30) → regime=MEAN_REVERTING ATR=0.1005% Kelly×1.00
  10:00:28 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  10:00:29 [INFO ] zisi.engine: [ENGINE] SOL/15m: [PRE-FETCH HIT] sol-updown-15m-1782460800 up=0.4250 dn=0.5750 spread=0.0200
  10:00:29 [INFO ] zisi.trader: [PAPER] BUY YES | 24 shares @ 0.4250 = $10.2000 | [UPDOWN][SOL][15m][SIGNAL] Solana Up or Down - June 26,
  10:00:29 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][SOL][15m][SIGNAL] Solana Up or Down - June 26, 4:00AM-4:15AM ET' (entry=0.4250) -> target 0.8800, stop -1.0
  10:00:29 [INFO ] zisi.main: [TRADE OPENED] SOL/15m UP | $10.20 @ 0.4250 | score=0.83 | SIGNAL
  10:00:29 [INFO ] zisi.main: [CORR] SOL/15m UP | $10.00 @ 0.4250 | shadow of BTC/15m [SIG] → logged as SIGNAL
  10:00:31 [WARNING] zisi.rtds.ws: [RTDS-WS] Watchdog: 180s timeout reached with no messages — triggering reconnect.
  10:00:31 [DEBUG] zisi.main: [HEARTBEAT] Heartbeat written successfully (trades=988, paused=False)
  10:00:31 [INFO ] zisi.rtds.ws: [RTDS-WS] Connecting to wss://ws-live-data.polymarket.com...
  ```

---



### Loss #145: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 10:00:35 (Hour: 10 SAST, UTC: 08:00:35)
- **Exit Time (SAST):** 2026-06-26 08:15:16
- **Entry Price:** 0.585 | **Exit Price:** 0.010 | **PnL:** $-9.78 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][XRP][15m][SIGNAL] XRP Up or Down - June 26, 4:00AM-4:15AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  10:00:34 [INFO ] zisi.main: [MAIN] ETH/5m SKIP (no_signal)
  10:00:34 [INFO ] zisi.main: [MAIN] XRP/5m: Signal evaluation retry window closed (elapsed=34.5s > 30.0s) — skip
  10:00:34 [DEBUG] zisi.metrics: Skip recorded — no_signal:
  10:00:34 [INFO ] zisi.main: [MAIN] XRP/5m SKIP (no_signal)
  10:00:34 [INFO ] zisi.main: [MAIN] DOGE/5m: Signal evaluation retry window closed (elapsed=34.5s > 30.0s) — skip
  10:00:34 [DEBUG] zisi.metrics: Skip recorded — no_signal:
  10:00:34 [INFO ] zisi.main: [MAIN] DOGE/5m SKIP (no_signal)
  10:00:34 [INFO ] zisi.main: [MAIN] ETH/15m: Signal evaluation retry window closed (elapsed=34.5s > 30.0s) — skip
  10:00:34 [DEBUG] zisi.metrics: Skip recorded — no_signal:
  10:00:34 [INFO ] zisi.main: [MAIN] ETH/15m SKIP (no_signal)
  10:00:35 [INFO ] zisi.main: [MAIN] BTC/5m: Signal evaluation retry window closed (elapsed=35.1s > 30.0s) — skip
  10:00:35 [DEBUG] zisi.metrics: Skip recorded — no_signal:
  10:00:35 [INFO ] zisi.main: [MAIN] BTC/5m SKIP (no_signal)
  10:00:35 [INFO ] zisi.engine: [ENGINE] XRP/15m: [PRE-FETCH HIT] xrp-updown-15m-1782460800 up=0.5850 dn=0.4150 spread=0.0200
  10:00:35 [INFO ] zisi.trader: [PAPER] BUY YES | 17 shares @ 0.5850 = $9.9450 | [UPDOWN][XRP][15m][SIGNAL] XRP Up or Down - June 26, 4:
  10:00:35 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][XRP][15m][SIGNAL] XRP Up or Down - June 26, 4:00AM-4:15AM ET' (entry=0.5850) -> target 0.8800, stop -1.0
  10:00:35 [INFO ] zisi.main: [TRADE OPENED] XRP/15m UP | $9.95 @ 0.5850 | score=0.83 | SIGNAL
  10:00:35 [INFO ] zisi.main: [MAIN] SOL/5m: Signal evaluation retry window closed (elapsed=35.3s > 30.0s) — skip
  10:00:35 [DEBUG] zisi.metrics: Skip recorded — no_signal:
  10:00:35 [INFO ] zisi.main: [MAIN] SOL/5m SKIP (no_signal)
  10:00:35 [INFO ] zisi.main: [CORR] XRP/15m UP | $10.00 @ 0.5850 | shadow of BTC/15m [SIG] → logged as SIGNAL
  ```

---



### Loss #146: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 10:00:40 (Hour: 10 SAST, UTC: 08:00:40)
- **Exit Time (SAST):** 2026-06-26 08:15:16
- **Entry Price:** 0.590 | **Exit Price:** 0.010 | **PnL:** $-9.86 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][DOGE][15m][SIGNAL] Dogecoin Up or Down - June 26, 4:00AM-4:15AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  10:00:35 [DEBUG] zisi.metrics: Skip recorded — no_signal:
  10:00:35 [INFO ] zisi.main: [MAIN] BTC/5m SKIP (no_signal)
  10:00:35 [INFO ] zisi.engine: [ENGINE] XRP/15m: [PRE-FETCH HIT] xrp-updown-15m-1782460800 up=0.5850 dn=0.4150 spread=0.0200
  10:00:35 [INFO ] zisi.trader: [PAPER] BUY YES | 17 shares @ 0.5850 = $9.9450 | [UPDOWN][XRP][15m][SIGNAL] XRP Up or Down - June 26, 4:
  10:00:35 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][XRP][15m][SIGNAL] XRP Up or Down - June 26, 4:00AM-4:15AM ET' (entry=0.5850) -> target 0.8800, stop -1.0
  10:00:35 [INFO ] zisi.main: [TRADE OPENED] XRP/15m UP | $9.95 @ 0.5850 | score=0.83 | SIGNAL
  10:00:35 [INFO ] zisi.main: [MAIN] SOL/5m: Signal evaluation retry window closed (elapsed=35.3s > 30.0s) — skip
  10:00:35 [DEBUG] zisi.metrics: Skip recorded — no_signal:
  10:00:35 [INFO ] zisi.main: [MAIN] SOL/5m SKIP (no_signal)
  10:00:35 [INFO ] zisi.main: [CORR] XRP/15m UP | $10.00 @ 0.5850 | shadow of BTC/15m [SIG] → logged as SIGNAL
  10:00:35 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  10:00:36 [DEBUG] zisi.arbitrage: [ARB] TCP connections warmed successfully.
  10:00:38 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  10:00:40 [INFO ] zisi.engine: [ENGINE] DOGE/15m: [PRE-FETCH HIT] doge-updown-15m-1782460800 up=0.5900 dn=0.4100 spread=0.1600
  10:00:40 [INFO ] zisi.trader: [PAPER] BUY YES | 17 shares @ 0.5900 = $10.0300 | [UPDOWN][DOGE][15m][SIGNAL] Dogecoin Up or Down - June
  10:00:40 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][DOGE][15m][SIGNAL] Dogecoin Up or Down - June 26, 4:00AM-4:15AM ET' (entry=0.5900) -> target 0.8800, stop -1.0
  10:00:40 [INFO ] zisi.main: [TRADE OPENED] DOGE/15m UP | $10.03 @ 0.5900 | score=0.83 | SIGNAL
  10:00:41 [INFO ] zisi.main: [CORR] DOGE/15m UP | $10.00 @ 0.5900 | shadow of BTC/15m [SIG] → logged as SIGNAL
  10:00:42 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  10:00:45 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  10:00:45 [INFO ] zisi.arbitrage: [ARB] Dynamic Volatility-Scaled Hurdle calibrated: 1.40% (ATR=121.04, Price=60551.99)
  ```

---



### Loss #147: UNK 5m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 12:00:09 (Hour: 12 SAST, UTC: 10:00:09)
- **Exit Time (SAST):** 2026-06-26 10:05:04
- **Entry Price:** 0.545 | **Exit Price:** 0.010 | **PnL:** $-13.38 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 26, 6:00AM-6:05AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  12:00:09 [INFO ] zisi.volatility_surface: [VolSurface] BTC → bias=neutral strength=0.000 oi=weak_rally sentiment=-0.100 modifier=1.000
  12:00:09 [DEBUG] zisi.whale_tracker: [WhaleTracker] BTC fetched 50 trades
  12:00:09 [INFO ] zisi.whale_tracker: [WhaleTracker] BTC → pressure=-1.000 dir=bearish whales=11 buy_vol=0 sell_vol=3580 multiplier=0.850
  12:00:09 [INFO ] zisi.edge_orchestrator: [EDGE] BTC UP | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=0.30 whale=0.75 sentiment=1.00 → boost=-0.180
  12:00:09 [INFO ] zisi.engine: [EDGE] BTC/5m Score adjusted by boost: 0.90 -> 0.72 (boost=-0.18)
  12:00:09 [INFO ] zisi.confluence_engine: [Confluence] BTC UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=32.97, Mom=-0.07%) | 5m=DOWN(RSI=17.88, Mom=-0.45%) | 15m=DOWN(RSI=25.47, Mom=-0.73%) | 1h=NEUTRAL(RSI=52.59, Mom=-0.97%)
  12:00:09 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=2/4 (MODERATE) boost=0.05 | 1m=NEUTRAL(RSI=32.97, Mom=-0.07%) | 5m=DOWN(RSI=17.88, Mom=-0.45%) | 15m=DOWN(RSI=25.47, Mom=-0.73%) | 1h=NEUTRAL(RSI=52.59, Mom=-0.97%)
  12:00:09 [INFO ] zisi.engine: [ENGINE] BTC/5m SIGNAL: UP | Score=0.72 | up=0.5450 dn=0.4550 | dual=False | Bitcoin Up or Down - June 26, 6:00AM-6:05AM ET
  12:00:09 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7802, fraction=0.1951)
  12:00:09 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.83 kelly_fraction=0.1951 | regime*1.20 anti*0.30 heat*1.00 whale*0.75 | -> $22.60 | cycle=$22.60/1 trades
  12:00:09 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $22.60
  12:00:09 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $22.35 (shares=41, conf=0.72, asset_w=1.00)
  12:00:09 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  12:00:09 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $22.35 → $13.41
  12:00:09 [INFO ] zisi.trader: [PAPER] BUY YES | 25 shares @ 0.5450 = $13.6250 | [UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 26,
  12:00:09 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 26, 6:00AM-6:05AM ET' (entry=0.5450) -> target 0.7200, stop -1.0
  12:00:09 [INFO ] zisi.main: [TRADE OPENED] BTC/5m UP | $13.63 @ 0.5450 | score=0.72 | SINGLE
  12:00:09 [INFO ] zisi.logger: [SIGNAL-EVAL] BTC | score=0.72 | type=REAL | conf=0.72
  12:00:10 [INFO ] zisi.main: [CORR-MAGNITUDE] BTC/5m lead UP move -0.0067% = 0.07x window range (need aligned and >= 0.40x) — no shadows this window
  12:00:10 [INFO ] zisi.regime_detector: [RegimeDetector] initialised — timeframe=15m ATR window=14 lookback=50 BB(20, 2.0)
  12:00:10 [DEBUG] zisi.regime_detector: [Regime] BTC bulk update (30) → regime=MEAN_REVERTING ATR=0.1587% Kelly×1.00
  ```

---



### Loss #148: UNK 5m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 12:10:18 (Hour: 12 SAST, UTC: 10:10:18)
- **Exit Time (SAST):** 2026-06-26 10:15:11
- **Entry Price:** 0.565 | **Exit Price:** 0.010 | **PnL:** $-6.10 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][SOL][5m][SINGLE] Solana Up or Down - June 26, 6:10AM-6:15AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  12:10:17 [INFO ] zisi.confluence_engine: [Confluence] SOL UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=52.05, Mom=0.04%) | 5m=DOWN(RSI=29.2, Mom=-0.10%) | 15m=NEUTRAL(RSI=40.31, Mom=-0.93%) | 1h=NEUTRAL(RSI=64.34, Mom=-1.20%)
  12:10:17 [INFO ] zisi.confluence_engine: [Confluence] SOL DOWN: score=1/4 (WEAK) boost=0.00 | 1m=NEUTRAL(RSI=52.05, Mom=0.04%) | 5m=DOWN(RSI=29.2, Mom=-0.10%) | 15m=NEUTRAL(RSI=40.31, Mom=-0.93%) | 1h=NEUTRAL(RSI=64.34, Mom=-1.20%)
  12:10:17 [INFO ] zisi.engine: [ENGINE] SOL/5m SIGNAL: UP | Score=0.72 | up=0.5650 dn=0.4350 | dual=False | Solana Up or Down - June 26, 6:10AM-6:15AM ET
  12:10:18 [INFO ] zisi.regime_detector: [RegimeDetector] initialised — timeframe=5m ATR window=14 lookback=50 BB(20, 2.0)
  12:10:18 [DEBUG] zisi.regime_detector: [Regime] BTC bulk update (30) → regime=MEAN_REVERTING ATR=0.0703% Kelly×1.00
  12:10:18 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7701, fraction=0.1925)
  12:10:18 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.77 kelly_fraction=0.1925 | regime*1.20 anti*0.30 heat*1.00 whale*1.10 | -> $22.51 | cycle=$22.51/1 trades
  12:10:18 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $22.51
  12:10:18 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $22.60 (shares=40, conf=0.72, asset_w=1.00)
  12:10:18 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  12:10:18 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $22.60 → $13.56
  12:10:18 [INFO ] zisi.main: [RISK] SIG/5m premium +35%: $18.31
  12:10:18 [INFO ] zisi.main: [RISK] SIGNAL trade size capped at $10.0: $18.31 -> $10.00
  12:10:18 [INFO ] zisi.main: [RISK] SOL/XRP Sizing calibrated to 60%: $6.00
  12:10:18 [INFO ] zisi.trader: [PAPER] BUY YES | 11 shares @ 0.5650 = $6.2150 | [UPDOWN][SOL][5m][SINGLE] Solana Up or Down - June 26,
  12:10:18 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][SOL][5m][SINGLE] Solana Up or Down - June 26, 6:10AM-6:15AM ET' (entry=0.5650) -> target 0.7200, stop -1.0
  12:10:18 [INFO ] zisi.main: [TRADE OPENED] SOL/5m UP | $6.21 @ 0.5650 | score=0.72 | SINGLE
  12:10:18 [INFO ] zisi.logger: [SIGNAL-EVAL] SOL | score=0.72 | type=REAL | conf=0.72
  12:10:18 [INFO ] zisi.rtds.ws: [RTDS-WS] Binance REST fallback: updated 5 prices
  12:10:19 [INFO ] zisi.arbitrage: [ARB] Dynamic Volatility-Scaled Hurdle calibrated: 1.37% (ATR=111.80, Price=59777.99)
  12:10:19 [INFO ] zisi.arbitrage: [ARB] Starting arbitrage scan cycle (spread hurdle: 1.37%)...
  ```

---



### Loss #149: UNK 5m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 12:25:08 (Hour: 12 SAST, UTC: 10:25:08)
- **Exit Time (SAST):** 2026-06-26 10:30:12
- **Entry Price:** 0.495 | **Exit Price:** 0.010 | **PnL:** $-7.27 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 26, 6:25AM-6:30AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  12:25:08 [INFO ] zisi.edge_orchestrator: [EDGE] BTC UP | regime=TRENDING(×0.30) confluence=0(+-0.10) heat=1.00 anti=0.30 whale=1.10 sentiment=1.00 → boost=-0.050
  12:25:08 [INFO ] zisi.engine: [EDGE] BTC/5m Score adjusted by boost: 0.80 -> 0.75 (boost=-0.05)
  12:25:08 [INFO ] zisi.confluence_engine: [Confluence] BTC UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=54.85, Mom=-0.03%) | 5m=NEUTRAL(RSI=12.22, Mom=-0.07%) | 15m=DOWN(RSI=27.52, Mom=-0.65%) | 1h=NEUTRAL(RSI=52.64, Mom=-0.96%)
  12:25:08 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=1/4 (WEAK) boost=0.00 | 1m=NEUTRAL(RSI=54.85, Mom=-0.03%) | 5m=NEUTRAL(RSI=12.22, Mom=-0.07%) | 15m=DOWN(RSI=27.52, Mom=-0.65%) | 1h=NEUTRAL(RSI=52.64, Mom=-0.96%)
  12:25:08 [INFO ] zisi.engine: [ENGINE] BTC/5m SIGNAL: UP | Score=0.75 | up=0.4950 dn=0.5050 | dual=False | Bitcoin Up or Down - June 26, 6:25AM-6:30AM ET
  12:25:08 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.8020, fraction=0.2005)
  12:25:08 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=1.02 kelly_fraction=0.2005 | regime*0.30 anti*0.30 heat*1.00 whale*1.10 | -> $12.54 | cycle=$12.54/1 trades
  12:25:08 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $12.54
  12:25:08 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $12.38 (shares=25, conf=0.75, asset_w=1.00)
  12:25:08 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  12:25:08 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $12.38 → $7.42
  12:25:08 [DEBUG] zisi.arbitrage: [ARB] TCP connections warmed successfully.
  12:25:08 [DEBUG] zisi.volatility_surface: [VolSurface] SOL OI = 10586615.71
  12:25:08 [INFO ] zisi.volatility_surface: [VolSurface] SOL → bias=neutral strength=0.000 oi=weak_rally sentiment=-0.100 modifier=1.000
  12:25:08 [INFO ] zisi.trader: [PAPER] BUY YES | 15 shares @ 0.4950 = $7.4250 | [UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 26,
  12:25:08 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 26, 6:25AM-6:30AM ET' (entry=0.4950) -> target 0.7200, stop -1.0
  12:25:08 [INFO ] zisi.main: [TRADE OPENED] BTC/5m UP | $7.42 @ 0.4950 | score=0.75 | SINGLE
  12:25:08 [INFO ] zisi.main: [LEADER-GUARD] DOGE/5m UP: blocked because BOTH leaders (BTC & ETH) are against the trade direction
  12:25:08 [DEBUG] zisi.metrics: Skip recorded — leader_corroboration_guard:
  12:25:08 [INFO ] zisi.main: [MAIN] DOGE/5m SKIP (leader_corroboration_guard)
  12:25:08 [INFO ] zisi.logger: [SIGNAL-EVAL] DOGE | score=0.70 | type=MISSED | conf=0.70
  ```

---



### Loss #150: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 12:30:09 (Hour: 12 SAST, UTC: 10:30:09)
- **Exit Time (SAST):** 2026-06-26 10:45:00
- **Entry Price:** 0.545 | **Exit Price:** 0.010 | **PnL:** $-9.10 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26, 6:30AM-6:45AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  12:30:09 [INFO ] zisi.whale_tracker: [WhaleTracker] BTC → pressure=-0.756 dir=bearish whales=17 buy_vol=1631 sell_vol=11743 multiplier=0.850
  12:30:09 [DEBUG] zisi.portfolio_heat: [PortfolioHeat] heat=0.0000 mult=1.00 positions=1
  12:30:09 [INFO ] zisi.edge_orchestrator: [EDGE] BTC UP | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=0.40 whale=0.75 sentiment=1.00 → boost=-0.180
  12:30:09 [INFO ] zisi.engine: [EDGE] BTC/15m Score adjusted by boost: 0.90 -> 0.72 (boost=-0.18)
  12:30:09 [INFO ] zisi.confluence_engine: [Confluence] BTC UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=30.09, Mom=-0.07%) | 5m=NEUTRAL(RSI=13.55, Mom=-0.03%) | 15m=DOWN(RSI=15.46, Mom=-0.45%) | 1h=NEUTRAL(RSI=52.56, Mom=-0.98%)
  12:30:09 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=1/4 (WEAK) boost=0.00 | 1m=NEUTRAL(RSI=30.09, Mom=-0.07%) | 5m=NEUTRAL(RSI=13.55, Mom=-0.03%) | 15m=DOWN(RSI=15.46, Mom=-0.45%) | 1h=NEUTRAL(RSI=52.56, Mom=-0.98%)
  12:30:09 [INFO ] zisi.engine: [ENGINE] BTC/15m SIGNAL: UP | Score=0.72 | up=0.5450 dn=0.4550 | dual=False | Bitcoin Up or Down - June 26, 6:30AM-6:45AM ET
  12:30:09 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7802, fraction=0.1951)
  12:30:09 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.83 kelly_fraction=0.1951 | regime*1.20 anti*0.40 heat*1.00 whale*0.75 | -> $22.60 | cycle=$22.60/1 trades
  12:30:09 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $22.60
  12:30:09 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $22.35 (shares=41, conf=0.72, asset_w=1.00)
  12:30:09 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  12:30:09 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $22.35 → $13.41
  12:30:09 [INFO ] zisi.main: [RISK] 15m size discount -30%: $9.38
  12:30:09 [INFO ] zisi.trader: [PAPER] BUY YES | 17 shares @ 0.5450 = $9.2650 | [UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26
  12:30:09 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26, 6:30AM-6:45AM ET' (entry=0.5450) -> target 0.8800, stop -1.0
  12:30:09 [DEBUG] zisi.whale_tracker: [WhaleTracker] XRP fetched 50 trades
  12:30:09 [INFO ] zisi.whale_tracker: [WhaleTracker] XRP → pressure=0.236 dir=neutral whales=11 buy_vol=4716 sell_vol=2913 multiplier=1.000
  12:30:09 [DEBUG] zisi.portfolio_heat: [PortfolioHeat] heat=0.0000 mult=1.00 positions=1
  12:30:09 [INFO ] zisi.main: [TRADE OPENED] BTC/15m UP | $9.27 @ 0.5450 | score=0.72 | SINGLE
  12:30:09 [INFO ] zisi.edge_orchestrator: [EDGE] XRP UP | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=0.40 whale=1.00 sentiment=1.03 → boost=-0.073
  ```

---



### Loss #151: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 12:30:17 (Hour: 12 SAST, UTC: 10:30:17)
- **Exit Time (SAST):** 2026-06-26 10:45:01
- **Entry Price:** 0.505 | **Exit Price:** 0.010 | **PnL:** $-9.41 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][ETH][15m][SINGLE] Ethereum Up or Down - June 26, 6:30AM-6:45AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  12:30:17 [INFO ] zisi.confluence_engine: [Confluence] ETH DOWN: score=2/4 (MODERATE) boost=0.05 | 1m=DOWN(RSI=35.26, Mom=-0.12%) | 5m=NEUTRAL(RSI=24.87, Mom=0.00%) | 15m=DOWN(RSI=13.73, Mom=-0.67%) | 1h=NEUTRAL(RSI=47.93, Mom=-1.15%)
  12:30:17 [INFO ] zisi.engine: [ENGINE] ETH/15m SIGNAL: UP | Score=0.72 | up=0.5050 dn=0.4950 | dual=False | Ethereum Up or Down - June 26, 6:30AM-6:45AM ET
  12:30:17 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7980, fraction=0.1995)
  12:30:17 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.98 kelly_fraction=0.1995 | regime*1.20 anti*0.40 heat*1.00 whale*0.75 | -> $22.60 | cycle=$22.60/1 trades
  12:30:17 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $22.60
  12:30:17 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $22.73 (shares=45, conf=0.72, asset_w=1.00)
  12:30:17 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  12:30:17 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $22.73 → $13.63
  12:30:17 [INFO ] zisi.main: [RISK] 15m size discount -30%: $9.54
  12:30:17 [DEBUG] zisi.whale_tracker: [WhaleTracker] SOL fetched 50 trades
  12:30:17 [INFO ] zisi.whale_tracker: [WhaleTracker] SOL → pressure=1.000 dir=bullish whales=3 buy_vol=834 sell_vol=0 multiplier=1.100
  12:30:17 [DEBUG] zisi.portfolio_heat: [PortfolioHeat] heat=0.0000 mult=1.00 positions=1
  12:30:17 [INFO ] zisi.edge_orchestrator: [EDGE] SOL UP | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=0.40 whale=1.10 sentiment=1.00 → boost=-0.050
  12:30:17 [INFO ] zisi.engine: [EDGE] SOL/15m Score adjusted by boost: 0.90 -> 0.85 (boost=-0.05)
  12:30:17 [INFO ] zisi.trader: [PAPER] BUY YES | 19 shares @ 0.5050 = $9.5950 | [UPDOWN][ETH][15m][SINGLE] Ethereum Up or Down - June 2
  12:30:17 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][ETH][15m][SINGLE] Ethereum Up or Down - June 26, 6:30AM-6:45AM ET' (entry=0.5050) -> target 0.8800, stop -1.0
  12:30:17 [INFO ] zisi.main: [TRADE OPENED] ETH/15m UP | $9.60 @ 0.5050 | score=0.72 | SINGLE
  12:30:17 [INFO ] zisi.confluence_engine: [Confluence] SOL UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=48.84, Mom=-0.07%) | 5m=NEUTRAL(RSI=24.22, Mom=0.07%) | 15m=DOWN(RSI=19.09, Mom=-0.66%) | 1h=NEUTRAL(RSI=64.24, Mom=-1.24%)
  12:30:17 [INFO ] zisi.confluence_engine: [Confluence] SOL DOWN: score=1/4 (WEAK) boost=0.00 | 1m=NEUTRAL(RSI=48.84, Mom=-0.07%) | 5m=NEUTRAL(RSI=24.22, Mom=0.07%) | 15m=DOWN(RSI=19.09, Mom=-0.66%) | 1h=NEUTRAL(RSI=64.24, Mom=-1.24%)
  12:30:17 [INFO ] zisi.engine: [ENGINE] SOL/15m SIGNAL: UP | Score=0.85 | up=0.4350 dn=0.5650 | dual=False | Solana Up or Down - June 26, 6:30AM-6:45AM ET
  12:30:17 [INFO ] zisi.logger: [SIGNAL-EVAL] ETH | score=0.72 | type=REAL | conf=0.72
  ```

---



### Loss #152: UNK 5m FV (NO)
- **Entry Time (SAST):** 2026-06-26 12:40:50 (Hour: 12 SAST, UTC: 10:40:50)
- **Exit Time (SAST):** 2026-06-26 10:45:02
- **Entry Price:** 0.335 | **Exit Price:** 0.010 | **PnL:** $-18.52 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][XRP][5m][FAIR_VAL] XRP Up or Down - June 26, 6:40AM-6:45AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  12:40:49 [INFO ] zisi.main: [MAIN] ETH/5m: Signal evaluation retry window closed (elapsed=49.7s > 30.0s) — skip
  12:40:49 [DEBUG] zisi.metrics: Skip recorded — no_signal:
  12:40:49 [INFO ] zisi.main: [MAIN] ETH/5m SKIP (no_signal)
  12:40:50 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.8496, fraction=0.2124)
  12:40:50 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=1.99 kelly_fraction=0.2124 | regime*1.20 anti*0.50 heat*1.00 whale*1.00 | -> $24.49 | cycle=$24.49/1 trades
  12:40:50 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $24.49
  12:40:50 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $24.46 (shares=73, conf=0.74, asset_w=1.00)
  12:40:50 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  12:40:50 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $31.79 → $19.07
  12:40:50 [INFO ] zisi.main: [RISK] XRP/5m corroboration_mult=1.3 → bet $19.07
  12:40:50 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.8450, fraction=0.2112)
  12:40:50 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=1.82 kelly_fraction=0.2112 | regime*1.20 anti*0.50 heat*1.00 whale*0.75 | -> $23.38 | cycle=$23.38/1 trades
  12:40:50 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $23.38
  12:40:50 [INFO ] zisi.trader: [PAPER] BUY NO | 57 shares @ 0.3350 = $19.0950 | [UPDOWN][XRP][5m][FAIR_VAL] XRP Up or Down - June 26, 6
  12:40:50 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $23.43 (shares=66, conf=0.73, asset_w=1.00)
  12:40:50 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][XRP][5m][FAIR_VAL] XRP Up or Down - June 26, 6:40AM-6:45AM ET' (entry=0.3350) -> target 0.7200, stop -1.0
  12:40:50 [INFO ] zisi.main: [TRADE OPENED] XRP/5m DOWN | $19.10 @ 0.3350 | score=0.98 | FAIR_VAL
  12:40:50 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  12:40:50 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $30.46 → $18.28
  12:40:50 [INFO ] zisi.main: [RISK] SOL/5m corroboration_mult=1.3 → bet $18.28
  12:40:50 [INFO ] zisi.main: [MAIN] SOL/5m COOLDOWN skip — next entry in 2.9s
  ```

---



### Loss #153: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 12:45:09 (Hour: 12 SAST, UTC: 10:45:09)
- **Exit Time (SAST):** 2026-06-26 11:00:03
- **Entry Price:** 0.505 | **Exit Price:** 0.010 | **PnL:** $-5.94 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26, 6:45AM-7:00AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  12:45:08 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=2/4 (MODERATE) boost=0.05 | 1m=NEUTRAL(RSI=30.45, Mom=-0.01%) | 5m=DOWN(RSI=20.05, Mom=-0.30%) | 15m=DOWN(RSI=7.35, Mom=-0.32%) | 1h=NEUTRAL(RSI=50.79, Mom=-1.29%)
  12:45:08 [INFO ] zisi.engine: [ENGINE] BTC/15m SIGNAL: UP | Score=0.80 | up=0.5050 dn=0.4950 | dual=False | Bitcoin Up or Down - June 26, 6:45AM-7:00AM ET
  12:45:08 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7980, fraction=0.1995)
  12:45:08 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.98 kelly_fraction=0.1995 | regime*1.20 anti*0.60 heat*1.00 whale*1.00 | -> $29.00 | cycle=$29.00/1 trades
  12:45:08 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $29.00
  12:45:08 [WARNING] zisi.engine: [SIZE] BTC/15m loss streak brake active (3 losses) -> halving size in adaptive Kelly
  12:45:08 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $14.64 (shares=29, conf=0.80, asset_w=1.00)
  12:45:08 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  12:45:08 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $14.64 → $8.79
  12:45:08 [INFO ] zisi.main: [RISK] 15m size discount -30%: $6.15
  12:45:08 [DEBUG] zisi.whale_tracker: [WhaleTracker] XRP fetched 50 trades
  12:45:08 [INFO ] zisi.whale_tracker: [WhaleTracker] XRP → pressure=0.968 dir=bullish whales=11 buy_vol=12461 sell_vol=200 multiplier=1.100
  12:45:09 [INFO ] zisi.edge_orchestrator: [EDGE] XRP UP | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=0.60 whale=1.10 sentiment=1.03 → boost=-0.023
  12:45:09 [INFO ] zisi.trader: [PAPER] BUY YES | 12 shares @ 0.5050 = $6.0600 | [UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26
  12:45:09 [INFO ] zisi.engine: [EDGE] XRP/15m Score adjusted by boost: 0.90 -> 0.88 (boost=-0.02)
  12:45:09 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26, 6:45AM-7:00AM ET' (entry=0.5050) -> target 0.8800, stop -1.0
  12:45:09 [INFO ] zisi.main: [TRADE OPENED] BTC/15m UP | $6.06 @ 0.5050 | score=0.80 | SINGLE
  12:45:09 [INFO ] zisi.confluence_engine: [Confluence] XRP UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=22.35, Mom=-0.05%) | 5m=DOWN(RSI=21.13, Mom=-0.47%) | 15m=DOWN(RSI=13.21, Mom=-0.37%) | 1h=NEUTRAL(RSI=47.6, Mom=-1.61%)
  12:45:09 [INFO ] zisi.confluence_engine: [Confluence] XRP DOWN: score=2/4 (MODERATE) boost=0.05 | 1m=NEUTRAL(RSI=22.35, Mom=-0.05%) | 5m=DOWN(RSI=21.13, Mom=-0.47%) | 15m=DOWN(RSI=13.21, Mom=-0.37%) | 1h=NEUTRAL(RSI=47.6, Mom=-1.61%)
  12:45:09 [INFO ] zisi.engine: [ENGINE] XRP/15m SIGNAL: UP | Score=0.88 | up=0.5250 dn=0.4750 | dual=False | XRP Up or Down - June 26, 6:45AM-7:00AM ET
  12:45:09 [DEBUG] zisi.cache: [CACHE] Hit for key: binance:klines:BTC:15m:2
  ```

---



### Loss #154: UNK 5m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 12:45:16 (Hour: 12 SAST, UTC: 10:45:16)
- **Exit Time (SAST):** 2026-06-26 10:50:02
- **Entry Price:** 0.545 | **Exit Price:** 0.010 | **PnL:** $-8.56 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 26, 6:45AM-6:50AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  12:45:16 [INFO ] zisi.whale_tracker: [WhaleTracker] BTC → pressure=0.047 dir=neutral whales=13 buy_vol=2297 sell_vol=2089 multiplier=1.000
  12:45:16 [DEBUG] zisi.portfolio_heat: [PortfolioHeat] heat=0.0000 mult=1.00 positions=1
  12:45:16 [INFO ] zisi.edge_orchestrator: [EDGE] BTC UP | regime=MEAN_REVERTING(×1.00) confluence=0(+-0.10) heat=1.00 anti=0.60 whale=1.00 sentiment=1.00 → boost=-0.100
  12:45:16 [INFO ] zisi.engine: [EDGE] BTC/5m Score adjusted by boost: 0.90 -> 0.80 (boost=-0.10)
  12:45:16 [INFO ] zisi.confluence_engine: [Confluence] BTC UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=30.45, Mom=-0.01%) | 5m=DOWN(RSI=20.05, Mom=-0.30%) | 15m=DOWN(RSI=7.35, Mom=-0.32%) | 1h=NEUTRAL(RSI=50.79, Mom=-1.29%)
  12:45:16 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=2/4 (MODERATE) boost=0.05 | 1m=NEUTRAL(RSI=30.45, Mom=-0.01%) | 5m=DOWN(RSI=20.05, Mom=-0.30%) | 15m=DOWN(RSI=7.35, Mom=-0.32%) | 1h=NEUTRAL(RSI=50.79, Mom=-1.29%)
  12:45:16 [INFO ] zisi.engine: [ENGINE] BTC/5m SIGNAL: UP | Score=0.80 | up=0.5450 dn=0.4550 | dual=False | Bitcoin Up or Down - June 26, 6:45AM-6:50AM ET
  12:45:16 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7802, fraction=0.1951)
  12:45:16 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.83 kelly_fraction=0.1951 | regime*1.00 anti*0.60 heat*1.00 whale*1.00 | -> $29.00 | cycle=$29.00/1 trades
  12:45:16 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $29.00
  12:45:16 [WARNING] zisi.engine: [SIZE] BTC/5m loss streak brake active (3 losses) -> halving size in adaptive Kelly
  12:45:16 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $14.72 (shares=27, conf=0.80, asset_w=1.00)
  12:45:16 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  12:45:16 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $14.72 → $8.83
  12:45:16 [INFO ] zisi.trader: [PAPER] BUY YES | 16 shares @ 0.5450 = $8.7200 | [UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 26,
  12:45:16 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][BTC][5m][SINGLE] Bitcoin Up or Down - June 26, 6:45AM-6:50AM ET' (entry=0.5450) -> target 0.7200, stop -1.0
  12:45:16 [INFO ] zisi.main: [TRADE OPENED] BTC/5m UP | $8.72 @ 0.5450 | score=0.80 | SINGLE
  12:45:16 [INFO ] zisi.logger: [SIGNAL-EVAL] BTC | score=0.80 | type=REAL | conf=0.80
  12:45:17 [INFO ] zisi.main: [CORR-MAGNITUDE] BTC/5m lead UP move +0.0134% = 0.13x window range (need aligned and >= 0.40x) — no shadows this window
  12:45:17 [DEBUG] zisi.trader: [PRICE-REFRESH] zisi_c21b9dad01b9: 0.5050 → 0.5150 (Δ+0.0100)
  12:45:18 [DEBUG] zisi.trader: [PRICE-REFRESH] zisi_0c343248486e: 0.5450 → 0.5050 (Δ-0.0400)
  ```

---



### Loss #155: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 13:15:09 (Hour: 13 SAST, UTC: 11:15:09)
- **Exit Time (SAST):** 2026-06-26 11:30:09
- **Entry Price:** 0.505 | **Exit Price:** 0.010 | **PnL:** $-13.37 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26, 7:15AM-7:30AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  13:15:09 [DEBUG] zisi.whale_tracker: [WhaleTracker] BTC fetched 50 trades
  13:15:09 [INFO ] zisi.whale_tracker: [WhaleTracker] BTC → pressure=0.725 dir=bullish whales=9 buy_vol=3730 sell_vol=595 multiplier=1.100
  13:15:09 [INFO ] zisi.edge_orchestrator: [EDGE] BTC UP | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=0.30 whale=1.10 sentiment=1.00 → boost=-0.050
  13:15:09 [INFO ] zisi.engine: [EDGE] BTC/15m Score adjusted by boost: 0.90 -> 0.85 (boost=-0.05)
  13:15:09 [INFO ] zisi.confluence_engine: [Confluence] BTC UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=62.5, Mom=-0.03%) | 5m=NEUTRAL(RSI=35.12, Mom=0.27%) | 15m=DOWN(RSI=16.43, Mom=-0.42%) | 1h=NEUTRAL(RSI=42.95, Mom=-1.75%)
  13:15:09 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=1/4 (WEAK) boost=0.00 | 1m=NEUTRAL(RSI=62.5, Mom=-0.03%) | 5m=NEUTRAL(RSI=35.12, Mom=0.27%) | 15m=DOWN(RSI=16.43, Mom=-0.42%) | 1h=NEUTRAL(RSI=42.95, Mom=-1.75%)
  13:15:09 [INFO ] zisi.engine: [ENGINE] BTC/15m SIGNAL: UP | Score=0.85 | up=0.5050 dn=0.4950 | dual=False | Bitcoin Up or Down - June 26, 7:15AM-7:30AM ET
  13:15:09 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7980, fraction=0.1995)
  13:15:09 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.98 kelly_fraction=0.1995 | regime*1.20 anti*0.30 heat*1.00 whale*1.10 | -> $33.00 | cycle=$33.00/1 trades
  13:15:09 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $33.00
  13:15:09 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $32.83 (shares=65, conf=0.85, asset_w=1.00)
  13:15:09 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  13:15:09 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $32.83 → $19.70
  13:15:09 [INFO ] zisi.main: [RISK] 15m size discount -30%: $13.79
  13:15:09 [INFO ] zisi.trader: [PAPER] BUY YES | 27 shares @ 0.5050 = $13.6350 | [UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26
  13:15:09 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26, 7:15AM-7:30AM ET' (entry=0.5050) -> target 0.8800, stop -1.0
  13:15:09 [INFO ] zisi.main: [TRADE OPENED] BTC/15m UP | $13.63 @ 0.5050 | score=0.85 | SINGLE
  13:15:09 [DEBUG] zisi.volatility_surface: [VolSurface] XRP OI = 352624737.80
  13:15:09 [INFO ] zisi.volatility_surface: [VolSurface] XRP → bias=neutral strength=0.000 oi=trend_confirm sentiment=0.300 modifier=1.027
  13:15:09 [DEBUG] zisi.volatility_surface: [VolSurface] ETH OI = 2298436.58
  13:15:09 [INFO ] zisi.volatility_surface: [VolSurface] ETH → bias=neutral strength=0.000 oi=trend_confirm sentiment=0.300 modifier=1.027
  ```

---



### Loss #156: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 13:45:09 (Hour: 13 SAST, UTC: 11:45:09)
- **Exit Time (SAST):** 2026-06-26 12:00:10
- **Entry Price:** 0.425 | **Exit Price:** 0.010 | **PnL:** $-9.13 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26, 7:45AM-8:00AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  13:45:09 [INFO ] zisi.confluence_engine: [Confluence] BTC DOWN: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=47.61, Mom=-0.05%) | 5m=NEUTRAL(RSI=45.31, Mom=0.00%) | 15m=NEUTRAL(RSI=18.12, Mom=0.18%) | 1h=NEUTRAL(RSI=42.36, Mom=-1.84%)
  13:45:09 [INFO ] zisi.engine: [ENGINE] BTC/15m SIGNAL: UP | Score=0.72 | up=0.4250 dn=0.5750 | dual=False | Bitcoin Up or Down - June 26, 7:45AM-8:00AM ET
  13:45:09 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.8261, fraction=0.2065)
  13:45:09 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=1.35 kelly_fraction=0.2065 | regime*1.00 anti*0.30 heat*1.00 whale*0.75 | -> $22.60 | cycle=$22.60/1 trades
  13:45:09 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $22.60
  13:45:09 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $22.52 (shares=53, conf=0.72, asset_w=1.00)
  13:45:09 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  13:45:09 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $22.52 → $13.51
  13:45:09 [INFO ] zisi.main: [RISK] 15m size discount -30%: $9.46
  13:45:09 [DEBUG] zisi.whale_tracker: [WhaleTracker] SOL fetched 50 trades
  13:45:09 [INFO ] zisi.whale_tracker: [WhaleTracker] SOL → pressure=0.160 dir=neutral whales=5 buy_vol=422 sell_vol=306 multiplier=1.000
  13:45:09 [DEBUG] zisi.portfolio_heat: [PortfolioHeat] heat=0.0000 mult=1.00 positions=1
  13:45:09 [INFO ] zisi.edge_orchestrator: [EDGE] SOL UP | regime=MEAN_REVERTING(×1.00) confluence=0(+-0.10) heat=1.00 anti=0.30 whale=1.00 sentiment=1.00 → boost=-0.100
  13:45:09 [INFO ] zisi.engine: [EDGE] SOL/15m Score adjusted by boost: 0.90 -> 0.80 (boost=-0.10)
  13:45:09 [INFO ] zisi.trader: [PAPER] BUY YES | 22 shares @ 0.4250 = $9.3500 | [UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26
  13:45:09 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][BTC][15m][SINGLE] Bitcoin Up or Down - June 26, 7:45AM-8:00AM ET' (entry=0.4250) -> target 0.8800, stop -1.0
  13:45:09 [DEBUG] zisi.trader: [MEMORY] Pruned 1 stale CLOSED positions from memory
  13:45:09 [INFO ] zisi.main: [TRADE OPENED] BTC/15m UP | $9.35 @ 0.4250 | score=0.72 | SINGLE
  13:45:09 [INFO ] zisi.confluence_engine: [Confluence] SOL UP: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=48.33, Mom=-0.17%) | 5m=NEUTRAL(RSI=43.48, Mom=-0.01%) | 15m=DOWN(RSI=14.44, Mom=-0.29%) | 1h=NEUTRAL(RSI=56.97, Mom=-3.09%)
  13:45:09 [INFO ] zisi.confluence_engine: [Confluence] SOL DOWN: score=1/4 (WEAK) boost=0.00 | 1m=NEUTRAL(RSI=48.33, Mom=-0.17%) | 5m=NEUTRAL(RSI=43.48, Mom=-0.01%) | 15m=DOWN(RSI=14.44, Mom=-0.29%) | 1h=NEUTRAL(RSI=56.97, Mom=-3.09%)
  13:45:09 [INFO ] zisi.engine: [ENGINE] SOL/15m SIGNAL: UP | Score=0.80 | up=0.4050 dn=0.5950 | dual=False | Solana Up or Down - June 26, 7:45AM-8:00AM ET
  ```

---



### Loss #157: UNK 15m SIG (YES)
- **Entry Time (SAST):** 2026-06-26 16:00:31 (Hour: 16 SAST, UTC: 14:00:31)
- **Exit Time (SAST):** 2026-06-26 14:15:22
- **Entry Price:** 0.600 | **Exit Price:** 0.010 | **PnL:** $-3.54 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][DOGE][15m][SINGLE] Dogecoin Up or Down - June 26, 10:00AM-10:15AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  16:00:31 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7500, fraction=0.1875)
  16:00:31 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.67 kelly_fraction=0.1875 | regime*1.20 anti*0.90 heat*1.00 whale*1.00 | -> $39.34 | cycle=$39.34/1 trades
  16:00:31 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $39.34
  16:00:31 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $39.60 (shares=66, conf=0.93, asset_w=1.00)
  16:00:31 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  16:00:31 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $51.48 → $30.89
  16:00:31 [INFO ] zisi.main: [RISK] DOGE/15m corroboration_mult=1.3 → bet $30.89
  16:00:31 [INFO ] zisi.main: [RISK] 15m size discount -30%: $21.62
  16:00:31 [INFO ] zisi.main: [RISK] STANDARD bet cap $21.62 -> $20.00
  16:00:31 [INFO ] zisi.main: [RISK] SIGNAL trade size capped at $10.0: $20.00 -> $10.00
  16:00:31 [INFO ] zisi.main: [RISK] Altcoin DOGE Sizing calibrated to 35% (max $35): $3.50
  16:00:31 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.7143, fraction=0.1786)
  16:00:31 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=0.54 kelly_fraction=0.1786 | regime*1.20 anti*0.90 heat*1.00 whale*1.00 | -> $40.00 | cycle=$40.00/1 trades
  16:00:31 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $40.00
  16:00:31 [INFO ] zisi.trader: [PAPER] BUY YES | 6 shares @ 0.6000 = $3.6000 | [UPDOWN][DOGE][15m][SINGLE] Dogecoin Up or Down - June
  16:00:31 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][DOGE][15m][SINGLE] Dogecoin Up or Down - June 26, 10:00AM-10:15AM ET' (entry=0.6000) -> target 0.8800, stop -1.0
  16:00:31 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $40.30 (shares=62, conf=0.97, asset_w=1.00)
  16:00:31 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  16:00:31 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $52.39 → $31.43
  16:00:31 [INFO ] zisi.main: [RISK] XRP/15m corroboration_mult=1.3 → bet $31.43
  16:00:31 [INFO ] zisi.main: [TRADE OPENED] DOGE/15m UP | $3.60 @ 0.6000 | score=0.93 | SINGLE
  ```

---



### Loss #158: UNK 5m SIG (NO)
- **Entry Time (SAST):** 2026-06-26 16:25:22 (Hour: 16 SAST, UTC: 14:25:22)
- **Exit Time (SAST):** 2026-06-26 14:30:21
- **Entry Price:** 0.485 | **Exit Price:** 0.010 | **PnL:** $-18.05 (MARKET_EXPIRED)
- **Title:** `[UPDOWN][ETH][5m][SINGLE] Ethereum Up or Down - June 26, 10:25AM-10:30AM ET`
- **Matched Signal Evaluation:** None found within 60s window.
- **Surrounding Log Excerpt:**
  ```
  16:25:22 [DEBUG] zisi.volatility_surface: [VolSurface] BTC funding rate = 0.000059
  16:25:22 [DEBUG] zisi.whale_tracker: [WhaleTracker] ETH fetched 50 trades
  16:25:22 [INFO ] zisi.whale_tracker: [WhaleTracker] ETH → pressure=1.000 dir=bullish whales=5 buy_vol=2291 sell_vol=0 multiplier=1.100
  16:25:22 [INFO ] zisi.edge_orchestrator: [EDGE] ETH DOWN | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=1.00 whale=0.75 sentiment=1.03 → boost=-0.153
  16:25:22 [INFO ] zisi.engine: [EDGE] ETH/5m Score adjusted by boost: 0.98 -> 0.83 (boost=-0.15)
  16:25:22 [INFO ] zisi.confluence_engine: [Confluence] ETH UP: score=2/4 (MODERATE) boost=0.05 | 1m=NEUTRAL(RSI=55.18, Mom=-0.13%) | 5m=UP(RSI=82.7, Mom=0.24%) | 15m=UP(RSI=61.5, Mom=2.24%) | 1h=NEUTRAL(RSI=51.0, Mom=1.30%)
  16:25:22 [INFO ] zisi.confluence_engine: [Confluence] ETH DOWN: score=0/4 (CONFLICT) boost=-0.10 | 1m=NEUTRAL(RSI=55.18, Mom=-0.13%) | 5m=UP(RSI=82.7, Mom=0.24%) | 15m=UP(RSI=61.5, Mom=2.24%) | 1h=NEUTRAL(RSI=51.0, Mom=1.30%)
  16:25:22 [INFO ] zisi.engine: [ENGINE] ETH/5m SIGNAL: DOWN | Score=0.83 | up=0.5150 dn=0.4850 | dual=False | Ethereum Up or Down - June 26, 10:25AM-10:30AM ET
  16:25:22 [INFO ] zisi.position_sizer: [KELLY-PILLAR-1] Quarter-Kelly (full=0.8058, fraction=0.2015)
  16:25:22 [INFO ] zisi.position_sizer: [KELLY] Trigger=Kelly | WR=90.0% payout=1.06 kelly_fraction=0.2015 | regime*1.20 anti*1.00 heat*1.00 whale*0.75 | -> $31.14 | cycle=$31.14/1 trades
  16:25:22 [INFO ] zisi.engine: [SIZE] Adaptive Kelly scaled by session multiplier 1.00x -> $31.14
  16:25:22 [INFO ] zisi.engine: [SIZE] Adaptive Kelly cost $31.04 (shares=64, conf=0.83, asset_w=1.00)
  16:25:22 [DEBUG] zisi.sentiment_daemon: [SENTIMENT] F&G=13 (Extreme Fear ≤20) → size ×0.60
  16:25:22 [INFO ] zisi.main: [SENTIMENT] F&G=13 extreme → size ×0.60: $31.04 → $18.62
  16:25:22 [INFO ] zisi.trader: [PAPER] BUY NO | 38 shares @ 0.4850 = $18.4300 | [UPDOWN][ETH][5m][SINGLE] Ethereum Up or Down - June 26
  16:25:22 [INFO ] zisi.trader: [SL-CALIB] Short-TF trade '[UPDOWN][ETH][5m][SINGLE] Ethereum Up or Down - June 26, 10:25AM-10:30AM ET' (entry=0.4850) -> target 0.7200, stop -1.0
  16:25:23 [INFO ] zisi.main: [TRADE OPENED] ETH/5m DOWN | $18.43 @ 0.4850 | score=0.83 | SINGLE
  16:25:23 [DEBUG] zisi.whale_tracker: [WhaleTracker] SOL fetched 50 trades
  16:25:23 [INFO ] zisi.whale_tracker: [WhaleTracker] SOL → pressure=-0.538 dir=bearish whales=5 buy_vol=606 sell_vol=2018 multiplier=0.850
  16:25:23 [DEBUG] zisi.portfolio_heat: [PortfolioHeat] heat=0.0000 mult=1.00 positions=1
  16:25:23 [INFO ] zisi.edge_orchestrator: [EDGE] SOL DOWN | regime=TRENDING(×1.20) confluence=0(+-0.10) heat=1.00 anti=1.00 whale=1.10 sentiment=1.03 → boost=-0.023
  ```

---
