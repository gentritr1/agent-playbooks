# Neon and Postgres measurements

**Source:** gold-pdf-bot memory `stability-branch.md` (2026-10-06), `neon-query-access.md` (2026-10-06), `neon-tls-and-setup.md` (2026-10-03/05); apollonia-events memory `apollonia-operations.md`, `apollonia-verification-scars.md`, `apollonia-neon-env.md` (2026-08-01); manga-reader memory `running-yomi-locally.md` (2026-07-13), `prod-migration-not-wired.md`; wordle memory `retention-plan-2026-08.md` (2026-08-03/05), `pglite-neon-bridge.md`.

## Measured
- gold-pdf-bot (smoke-test branch, through the pooler): first connection (Neon wake) 1.93 s, "so the old 2 s limit was nearly hit and 4 s is justified"; insert + update 0.45 s; `SET LOCAL statement_timeout = 1s` active through the pooler; `pg_sleep(3)` cancelled after 1.24 s. A startup `options` setting was avoided because it may be refused on the pooled URL.
- gold-pdf-bot: every Neon URL needs `sslmode=verify-full&sslrootcert=system`; smoke tests run on an auto-delete branch, never production.
- apollonia-events 2026-08-01: `/` is statically generated and "returns 200 from the CDN even with the database completely down — which happened three times on 2026-08-01". One resilience "test" "passed only because Neon had quietly recovered mid-run"; resilience is proved by building against a dead URL.
- apollonia-events: `DATABASE_URL` (pooled) and `DIRECT_URL` must be the same endpoint ± `-pooler`; a bad `DATABASE_URL` is a hard build failure under Next prerendering, on Vercel too (failed twice). No migrations; `db push` is manual.
- manga-reader 2026-07-13: "prepared statement s0 already exists" behind the proxy; the real fix is `&pgbouncer=true`. The build never runs `prisma migrate deploy`, and SQL applied by hand in production is not in `_prisma_migrations` (code-read finding, unresolved).
- wordle: Neon serverless-driver SQL runs in CI against WASM Postgres through a fetch shim (24, later 35, conformance tests); the bridge serialises statements, so interleaving is unproven.

## Inferred, not metered
- gold-pdf-bot (plan read 2026-10-06): 100 CU-h/month, scale-to-zero after 5 min; any SQL wakes compute for ~5 min, "~0.021 CU-h per isolated query at 0.25 CU (inferred)".
- wordle: "billing = awake-hours×CU not queries"; anonymous health pollers would "pin Neon compute ~95% of free CU-hours" (a model, not a bill).
