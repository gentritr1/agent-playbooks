# Monitoring critical modules (incident 1, gold-pdf-bot)

**Source:** gold-pdf-bot `docs/INCIDENTS.md` (incident 1, 2026-10-08), `tests/test_reliability.py`, `docs/ALERTS_ROLLOUT.md` section 11; gold-pdf-bot memory `neon-tls-and-setup.md`, `neon-query-access.md`, `feedback-monitoring-rule.md` (2026-10-08); Vercel log exports of that day (requests, status codes and the `timing` lines only).

## What happened
- A Neon role password was reset after it leaked into a chat. The project docs said the webhook used a write-only role; the live variable used the owner role. The variable was edited but not redeployed.
- About 3 hours with nothing stored: 1 bot alert (four tries, TradingView's resends), the 16:00 candle batch (four 503s), the 16:30 check-in (not stored and not delivered).
- The check-in answered **200** with `connect_ms: 247` and no `insert_ms`: the login was refused, the webhook still tried Telegram, and Telegram's failure reason was lost because only the database keeps it.
- The dashboard read only the database (through its own role, which stayed healthy), so it showed "Missing" without a reason. A probe on the dashboard's role would have stayed green.
- Hobby keeps runtime logs for 1 hour; the cause was found from two exported log CSVs, TradingView's `last_fire_time`, and a local read-only login check.

## Measured
- psycopg 3 connection failures carry no SQLSTATE; the label has to come from the driver text, printed as a fixed word (never the text itself, which names the user and host). Neon answers "password authentication failed" both for a wrong password and for an unknown endpoint host.
- A wrong password costs no compute: Neon's proxy checks the role secret before waking the compute (proxy source `auth/backend/mod.rs`, read 2026-10-08); the refusal took 247 ms.
- Cost of a scheduled check on the free tiers (Neon free 100 CU-h/month; one wake ≈ 0.021 CU-h): a database pinger every 5 min ≈ 180 CU-h/month, over the limit; every 2 h ≈ 7.6; on click ≈ 0.02 per press. Vercel Hobby cron runs once a day (±59 min). Existing traffic (alerts, a 2-hourly recorder batch, two daily check-ins) was the zero-cost monitor.
- Fix and drills: a reason label in every log line and in the next outgoing message, a System page that works without the database (settings on every page, a live check with the module's own address, Telegram getMe/getChat without sending). Each of the 7 new checks was broken on purpose once and its test failed (7 of 7).

## Inferred
- Five questions per critical module (alive, why, where and how fast, cost, drill) would have caught every step of the chain before it shipped; only the drills were run.
