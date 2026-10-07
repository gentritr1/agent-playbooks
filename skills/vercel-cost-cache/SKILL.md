---
name: vercel-cost-cache
description: Use before Vercel deploys, vercel.json headers or rewrites, Cache-Control, static assets or service workers, or Vercel cost work.
---

# Vercel cost and caching

Vercel bills bandwidth, edge requests (a CDN HIT still counts), function invocations and duration, and image transformations; only a request the browser never makes is free. We have measured request counts, headers and latency on our sites, but no billing data: cost claims below are inferred.

### VERC-001 · Hashed assets are immutable; HTML revalidates
- **Rule:** Serve content-hashed files with `public, max-age=31536000, immutable`, never change a file's bytes under the same name, and serve HTML with `max-age=0, must-revalidate`.
- **Kind:** invariant — why: the wrong pairing either re-requests every asset on every visit or serves stale bytes for a year.
- **Evidence:** morse-code-trainer 2026-08-23: reload went from 27 requests to 1, `x-vercel-cache: HIT`, HTML 304; wordle: screenshot files changed bytes under an immutable rule → [headers](evidence/headers.md)
- **Confidence:** VERIFIED
- **Gate:** `curl -sI` on one URL per asset class shows those headers; a changed asset has a new filename
- **Valid while:** `ctx:vercel` · last_validated: 2026-08-23
- **Source:** VERC-001

### VERC-002 · Every header rule matches a real path, every asset class has one
- **Rule:** Prove each `vercel.json` header `source` against a real deployed URL, and give every asset class a rule.
- **Kind:** invariant — why: a rule that matches nothing fails silently, and an SPA catch-all answers missing files with HTML and 200.
- **Evidence:** snaxx-tech 2026-08-07: `/videos/*` had no rule, so a 6 MB hero revalidated on every visit; a missing image returned the app shell with 200 → [headers](evidence/headers.md)
- **Confidence:** VERIFIED
- **Gate:** per pattern, `curl -sI` on a real URL shows the rule's header; a missing asset path is not served as `text/html` 200
- **Valid while:** `ctx:vercel` · last_validated: 2026-08-07
- **Source:** VERC-002

### VERC-003 · Inspect the build output before the first deploy
- **Rule:** Before a new or changed project config deploys, know exactly which files it publishes.
- **Kind:** invariant — why: a preset without an output directory publishes the repository root, source and docs included.
- **Evidence:** gold-pdf-bot 2026-10-04: preset "Other" without `outputDirectory` would publish 98 files including code and docs → [headers](evidence/headers.md)
- **Confidence:** VERIFIED
- **Gate:** a local `vercel build` output lists only intended public files; a config test pins `outputDirectory`
- **Valid while:** `ctx:vercel` · Vercel CLI · last_validated: 2026-10-04
- **Source:** VERC-003

### VERC-004 · A route that could be a file should be a file
- **Rule:** Make a page static or cached unless its response depends on the request, and check the build marks it so.
- **Kind:** heuristic — goal: fewer function invocations and lower latency per visit; override: stronger case evidence, stated in the report; expires: 2026-12-08
- **Evidence:** apollonia-events 2026-09-09: a route reading `searchParams` with an uncached Neon query rendered on every request, ~345 ms (298–704, n=5) vs ~209 ms prerendered → [functions](evidence/functions.md)
- **Confidence:** VERIFIED — latency measured from one location; invocation cost inferred
- **Gate:** the build output marks the route static or ISR, and a repeat request shows `x-vercel-cache: HIT`
- **Valid while:** `ctx:vercel` `ctx:web` · Next.js App Router · last_validated: 2026-09-09
- **Source:** VERC-004

### VERC-005 · Name the bill axis and requests per visit before optimising
- **Rule:** State which billed axis a change targets and the expected requests per visit before and after, then count them.
- **Kind:** heuristic — goal: optimise the axis that actually costs money; override: stronger case evidence, stated in the report; expires: 2026-11-21
- **Evidence:** morse-code-trainer 2026-08-23: server-log request counts cold 27 / reload 1 were the measurable proxy; no project has metered billing data → [functions](evidence/functions.md)
- **Confidence:** INFERRED — no Vercel usage or billing export was ever measured
- **Gate:** the report gives requests per visit before and after from logs or a browser trace with cache enabled
- **Valid while:** `ctx:vercel` · last_validated: 2026-08-23
- **Source:** VERC-005

## Gates before you report done
`curl -sI` per asset class (001, 002); missing-asset check (002); `vercel build` output listing (003); static/ISR marker (004); requests per visit (005).

## Not covered / defer to
Usage metrics and audits of deployed apps: `vercel-optimize`. Neon cold starts behind functions: `data-persistence`.
