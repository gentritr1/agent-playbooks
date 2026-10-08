# Functions, latency and what we have not measured

**Source:** `~/.claude/CLAUDE.md` §8; apollonia-events memory `reserve-route-is-uncached.md` (2026-09-09), `next-level-implementation-status.md` (2026-09-11), `apollonia-verification-scars.md` (2026-08-01); gold-pdf-bot memory `paper-entries-release.md`, `stability-branch.md` (2026-10-05/06), `docs/INCIDENTS.md` incident 1 and `docs/ALERTS_ROLLOUT.md` section 11 (2026-10-08); morse-code-trainer memory `deploy-caching.md` (2026-08-23).

- apollonia-events (Next.js on Vercel, n=5, one location): prerendered routes `x-vercel-cache: HIT` ~209 ms; `/reserve`, which reads `searchParams` server-side and runs an uncached Neon query, ~345 ms (range 298–704). Homepage RSC prefetch then triggers invocations. A 300 s cache was added; the route stayed dynamic, so the fix is partial.
- apollonia-events: `next/image` returned 200 and still painted nothing at a high device pixel ratio; small fixed marks set `unoptimized`, noted as saving image-optimisation quota (not metered).
- gold-pdf-bot: a Vercel function plus a cold Neon wake against a caller's ~3 s webhook budget; arrival delays of 3.3–8.8 s were measured, but the note says its own processing time is not measurable from those rows; "worst case ≈ 8 s" is computed, not measured.

## Not measured anywhere in our sources
Vercel usage or billing exports, function duration metrics, edge middleware. Cost statements in this skill are therefore INFERRED from §8 and request counts.

## A changed variable is a deploy (gold-pdf-bot, 2026-10-08)
- A database password was changed and the variable edited at about 14:10; the running build kept the old value until a redeploy at 15:31, and the 14:15 alert was lost.
- The redeploy carried Neon's copy-button format (`?sslmode=require&channel_binding=require`); the code's `verify-full` check refused it before any network call (`connect_ms: 0`, four 503s at 16:00). The next redeploy carried a password production refused (247 ms, no insert). A local read-only login with the exact value (`LOGIN OK as <role>`) before pasting fixed it in one more redeploy.
- Vercel swaps deployments atomically and TradingView resends a 5xx, so the rotation did not need the market pause; it needed the steps in one go: test, save, redeploy, confirm the next stored request.
