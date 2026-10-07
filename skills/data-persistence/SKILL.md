---
name: data-persistence
description: Before persisted-data or save-schema changes, migrations, Neon/Postgres URLs, timeouts or pooling, health checks, or DB cost estimates.
---

# Data and persistence (Neon / Postgres and client saves)

Only what our projects measured. For Neon features and setup, defer to the `neon-postgres` skill.

### DATA-001 · Schema changes check migration and wipe risk first
- **Rule:** Before changing any persisted shape, write the migration and a test that loads the previous version's data through the real load path.
- **Kind:** invariant — why: additive fields and slow reads have wiped user saves, and helper-only tests missed it.
- **Evidence:** planet-drop 2026-07-13: a field added without a schema bump would checksum-wipe every save (second firing); geoguesser 2026-09-09: a slow cold read wiped the profile → [persistence](evidence/persistence.md)
- **Confidence:** VERIFIED
- **Gate:** a fixture saved by the previous release loads through the production load function with every field intact; a downgrade test leaves the new data untouched
- **Valid while:** any persisted store · last_validated: 2026-10-01
- **Source:** DATA-001

### DATA-002 · Timeouts cover a Neon wake
- **Rule:** Set connect timeouts above the cold-wake time and bound each statement with `SET LOCAL statement_timeout`.
- **Kind:** fact — the first connection after scale-to-zero took 1.93 s; startup options may be refused on the pooled URL.
- **Evidence:** gold-pdf-bot 2026-10-06: wake 1.93 s against a 2 s limit (raised to 4 s); `pg_sleep(3)` cancelled after 1.24 s through the pooler → [neon](evidence/neon.md)
- **Confidence:** VERIFIED
- **Gate:** a smoke run on a disposable branch logs first-connect time below the timeout and a cancelled `pg_sleep`
- **Valid while:** `ctx:neon` · free plan, scale-to-zero 5 min · last_validated: 2026-10-06
- **Source:** DATA-002

### DATA-003 · Health checks touch the database
- **Rule:** Point uptime checks at an endpoint that queries the database, and test resilience against a dead database URL.
- **Kind:** invariant — why: a prerendered page answered 200 while the database was down three times in one day.
- **Evidence:** apollonia-events 2026-08-01: `/` stayed 200 from the CDN through three outages; a "resilience test" passed only because Neon recovered mid-run → [neon](evidence/neon.md)
- **Confidence:** VERIFIED
- **Gate:** the health endpoint returns non-200 when its database URL points at a dead host
- **Valid while:** `ctx:postgres` · last_validated: 2026-08-01
- **Source:** DATA-003

### DATA-004 · Pooled for the app, direct for migrations
- **Rule:** Use the direct URL for migrations and prepared statements (or `pgbouncer=true`), and keep pooled and direct URLs on the same endpoint.
- **Kind:** fact — the pooler multiplexes sessions, so named prepared statements collide; a bad URL fails a prerendering build.
- **Evidence:** manga-reader 2026-07-13: "prepared statement already exists" fixed by `pgbouncer=true`; apollonia-events: a bad `DATABASE_URL` failed the build twice → [neon](evidence/neon.md)
- **Confidence:** VERIFIED
- **Gate:** migrate commands read `DIRECT_URL`; the two URLs differ only by `-pooler`
- **Valid while:** `ctx:postgres` · Prisma behind a Neon pooler · last_validated: 2026-08-01
- **Source:** DATA-004

### DATA-005 · Neon cost follows awake time, not query count
- **Rule:** Batch database reads and remove anonymous pollers before tuning queries for cost.
- **Kind:** heuristic — goal: stay inside the plan's compute-hours; override: stronger case evidence, stated in the report; expires: 2027-01-04
- **Evidence:** gold-pdf-bot 2026-10-06: any query wakes compute for ~5 min (~0.021 CU-h each at 0.25 CU); wordle: health pollers modelled to pin ~95 % of free CU-hours → [neon](evidence/neon.md)
- **Confidence:** INFERRED — modelled from plan documentation, never metered
- **Gate:** the report states queries per hour and expected awake hours before and after
- **Valid while:** `ctx:neon` · Neon free plan read 2026-10-06 · last_validated: 2026-10-06
- **Source:** DATA-005

## Gates before you report done
Previous-version fixture through the real load path (001); timeouts above wake time (002); health endpoint fails on a dead URL (003); migrations on the direct URL (004).

## Not covered / defer to
Neon setup, branching, pooling and SDKs: `neon-postgres`; egress: `neon-postgres-egress-optimizer`. ORM migrations: `prisma-expert`, `database-migration`.
