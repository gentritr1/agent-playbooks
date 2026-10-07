# Red-green, mutation teeth and positive controls

**Source:** arrows-game reports ADMOB-B, ADMOB-C (2026-09-24), ART-SKINS-08 (2026-10-02), FINAL-REVIEW (2026-09-27); arrows-game `docs/engineering-lessons.md` (W5-17 follow-up 2026-10-06, HALLOWEEN-01 2026-10-04); arrows-game memory `detector-needs-positive-control.md` (2026-09-19); geoguesser-app memory `unreachable-usually-means-untested.md` (2026-10-02), `gates-recompute-never-trust-report-flags.md` and `every-gate-we-write-ships-a-silent-pass.md` (2026-09-16..10-04); secret-dictator-v2 memory `warm-budget-and-anti-tell.md` (2026-08-10); tondo memory `cdp-capture-harness.md` (2026-09-09); battleship memory `fleet-review-scars.md` (2026-07-16).

## Teeth
- ADMOB-B: one mutation per guard, suite run, file restored and `cmp`-checked; every guard caught (e.g. "Pacing reset on IMPRESSION | 4").
- ADMOB-C: the wiring passed on its first run, "so its proof is the mutations below" (6/6 caught).
- ART-SKINS-08: 21 new polish assertions fail on the restored starting tree (`checks/base-red.txt`) before passing.
- W5-17: removing the clamp under test failed 7 tests; a flattening helper had added an implied `Z`, which made a "loop is closed" assertion pass for any path.
- FINAL-REVIEW: after a wiring change `wired` was always true, so `expect(GEN_V2_ENABLED).toBe(false)` never ran.
- secret-dictator-v2: all seven mutants first reported clean; rule: assert `caught > 0` per mutant.
- geoguesser-app: ten wiring sites called "unreachable"; a 20-line source-scan test killed all ten.
- battleship: "A criterion that passes on the pre-fix tree proves nothing."

## Positive controls and primary data
- arrows-game W6-07 (2026-09-19): "0/10 crash records survive" came from grepping a log sink registered only under `__DEV__` in a release build; the logcats held 0 `[telemetry]` lines of any kind.
- HALLOWEEN-01: R8 renames helper classes, so a dex string search sees only the manifest-kept class; a zero for the others is blind, not proof.
- geoguesser-app C1a (2026-09-16): a coverage check trusted the report's own `reconciled` flag and passed n=240 against a table needing 18,432; across 16 instances the rule became "attack every gate with synthetic input; recompute from primary data".
- tondo: a harness attached to a zombie Chrome produced a vacuous pass, "3/3 surviving with ZERO repaints".
