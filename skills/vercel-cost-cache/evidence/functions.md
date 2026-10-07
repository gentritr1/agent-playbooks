# Functions, latency and what we have not measured

**Source:** `~/.claude/CLAUDE.md` §8; apollonia-events memory `reserve-route-is-uncached.md` (2026-09-09), `next-level-implementation-status.md` (2026-09-11), `apollonia-verification-scars.md` (2026-08-01); gold-pdf-bot memory `paper-entries-release.md`, `stability-branch.md` (2026-10-05/06); morse-code-trainer memory `deploy-caching.md` (2026-08-23).

- apollonia-events (Next.js on Vercel, n=5, one location): prerendered routes `x-vercel-cache: HIT` ~209 ms; `/reserve`, which reads `searchParams` server-side and runs an uncached Neon query, ~345 ms (range 298–704). Homepage RSC prefetch then triggers invocations. A 300 s cache was added; the route stayed dynamic, so the fix is partial.
- apollonia-events: `next/image` returned 200 and still painted nothing at a high device pixel ratio; small fixed marks set `unoptimized`, noted as saving image-optimisation quota (not metered).
- gold-pdf-bot: a Vercel function plus a cold Neon wake against a caller's ~3 s webhook budget; arrival delays of 3.3–8.8 s were measured, but the note says its own processing time is not measurable from those rows; "worst case ≈ 8 s" is computed, not measured.

## Not measured anywhere in our sources
Vercel usage or billing exports, function duration metrics, edge middleware. Cost statements in this skill are therefore INFERRED from §8 and request counts.
