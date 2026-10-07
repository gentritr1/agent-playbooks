# Headers, rewrites and build output on Vercel

**Source:** `~/.claude/CLAUDE.md` §8; morse-code-trainer memory `deploy-caching.md` (2026-08-23); snaxx-tech memory `snaxxtech-hosting-and-app-ads.md` (2026-07-27, audited 2026-08-07); wordle memory `retention-plan-2026-08.md` (2026-08-03 review), `art-asset-pipeline.md`; form-studio memory `form-design-direction.md` (2026-10-02); gold-pdf-bot memory `vercel-deploy-gotchas.md` (2026-10-04).

## Measured (live on Vercel)
- morse-code-trainer: server-log request counts (what Vercel bills as edge requests): unbuilt root cold 27 / reload 27 (25 × 304) / fresh return 26; `dist/` with headers cold 27 / reload 1 / fresh return 1. Live: all four asset classes `public, max-age=31536000, immutable` with `x-vercel-cache: HIT`, including the `:hash([0-9a-f]{8})` patterns; the document `public, max-age=0, must-revalidate` revalidates 304 / 0 bytes; deployed `index.html` byte-identical to a local build.
- morse-code-trainer: a measurement harness that disables the HTTP cache "silently destroys any cache measurement".
- snaxx-tech (curl against production): with a catch-all rewrite to `/index.html`, static files still win, but a missing file returns `text/html` 200 (the app shell). `/videos/*` had no rule, so the 6 MB hero revalidated on every visit; the rule was added 2026-08-07.

## Review findings
- wordle (2026-08-03): screenshot `-v1` files changed content under an immutable cache-control rule. A new asset needs the immutable header rule, the service-worker shell entry and a versioned filename.
- form-studio (2026-10-02): header rules asserted against real paths in a test; live `curl -sI` verification still open because the repo is not connected to a Vercel project (not verified live).

## Build output
- gold-pdf-bot (2026-10-04): preset "Other" without `outputDirectory` publishes the whole repo root as static files (98 files including code and docs); a Python preset breaks `/api`; `ignoreCommand` must compare against `$VERCEL_GIT_PREVIOUS_SHA`. Verified with a local `vercel build`, now pinned by a config test.
