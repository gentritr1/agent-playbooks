# Numbers quoted from briefs, and type-checking tests

**Source:** arrows-game `docs/engineering-lessons.md` (W3-20 and HEADER-FIT, 2026-10-06); `~/.claude/CLAUDE.md` §6 red flag on unmeasured thresholds; lucky-shelf memory `m7-round-review.md` (2026-07-08); morse-code-trainer memory `deploy-caching.md` (2026-08-23); arrows-game memory `speed-audit-2026-10-07.md`.

- W3-20: a brief asked for tiers "matching today's 3/2/1 cycle share" (1/2, 1/3, 1/6); the shipped cycle is N, N, H, N, N, SH = 4/6, 1/6, 1/6. The two cut sets differ (88/133 vs 95/133). The brief's "worst board" index had also been re-dealt by later changes.
- HEADER-FIT: the brief's jest baseline (143 suites / 2,408 tests) still counted a removed suite; HEAD was 142 / 2,396.
- lucky-shelf: thresholds written into a brief without live data caught 84 % of days; the 4th such firing promoted the rule to the global harness.
- morse-code-trainer: a brief predicted "a few KB" from minification; stripping comments and indentation took `dist/` from 84.5 KB to 54.6 KB brotli (−35 %).
- arrows-game speed audit (2026-10-07): the controller's guess that builds were the main time sink was wrong; builds were 6.2 % of active helper time.
- W3-20 also observed: the `ui` jest project (jest-expo) does not type-check; the tier-label tests passed in jest while `tsc --noEmit` failed on them.
