# Red-green, mutation teeth and positive controls

**Source:** arrows-game reports ADMOB-B, ADMOB-C (2026-09-24), ART-SKINS-08 (2026-10-02), FINAL-REVIEW (2026-09-27); arrows-game `docs/engineering-lessons.md` (W5-17 follow-up 2026-10-06, HALLOWEEN-01 2026-10-04); arrows-game memory `detector-needs-positive-control.md` (2026-09-19); geoguesser-app memory `unreachable-usually-means-untested.md` (2026-10-02), `gates-recompute-never-trust-report-flags.md` and `every-gate-we-write-ships-a-silent-pass.md` (2026-09-16..10-04); secret-dictator-v2 memory `warm-budget-and-anti-tell.md` (2026-08-10); tondo memory `cdp-capture-harness.md` (2026-09-09) and `brief-predicted-red-is-a-hypothesis.md` (2026-10-10); tondo `.superpowers/sdd/2026-10-10-crew-retention/` `progress.md`, `task-2-report.md` … `task-8-report.md` (mutant tables and gate sabotage runs); battleship memory `fleet-review-scars.md` (2026-07-16).

## Teeth
- ADMOB-B: one mutation per guard, suite run, file restored and `cmp`-checked; every guard caught (e.g. "Pacing reset on IMPRESSION | 4").
- ADMOB-C: the wiring passed on its first run, "so its proof is the mutations below" (6/6 caught).
- ART-SKINS-08: 21 new polish assertions fail on the restored starting tree (`checks/base-red.txt`) before passing.
- W5-17: removing the clamp under test failed 7 tests; a flattening helper had added an implied `Z`, which made a "loop is closed" assertion pass for any path.
- FINAL-REVIEW: after a wiring change `wired` was always true, so `expect(GEN_V2_ENABLED).toBe(false)` never ran.
- secret-dictator-v2: all seven mutants first reported clean; rule: assert `caught > 0` per mutant.
- geoguesser-app: ten wiring sites called "unreachable"; a 20-line source-scan test killed all ten.
- battleship: "A criterion that passes on the pre-fix tree proves nothing."

## Plan-written tests (tondo crew-retention, 2026-10-10)
The plan gave each task its tests verbatim; implementers ran mutants against them before adding any of their own. Counts are the mutant rows in each report.

| Task | Mutants run on the plan's tests | Survived | What the survivors exposed | After the added tests |
|---|---|---|---|---|
| T2 (reviewer's run) | 2 | 1 | `Math.ceil(elapsed)` slack is always ≥ 1, so a connect burst of 65 passed | fix round: 8 rows (M1–M7), all caught |
| T3 | 4 | 2 | classify precedence; `run()` state checked only through `publicStatus()` | both caught; fix round 13 of 13 caught |
| T4 | 7 | 2 | member sort order; uppercase hex accepted as a device secret | both caught; fix round 8 of 8 |
| T5 | 12 | 7 | record built after the await, device never reaching the store through `index.js`, read budget unspent, `/health` querying the database | all caught after targeted tests, one of them a new over-the-wire test; fix round 8 of 8 |
| T6 | 9 | 2 | bad writes hidden because reads repair them | both caught by one raw-storage test |

- T3–T6: 13 of 32 mutants survived the plan's own tests; T2 adds 1 of 2. Every survivor was caught once a targeted test or assertion was added.
- A plan test was also wrong, not only weak (T4): it counted a name across the whole shared database, where sibling fixtures legitimately create the same name, so a correct implementation failed 8 passed / 1 failed until the count was scoped to the crew under test. One firing; kept here, not a rule.
- The red run is not the proof (T2): the plan predicted the pre-fix failure "11th after reconnect: No table has that code."; it failed at "attempt 6: Too many wrong table codes", because an older per-socket cap of 5 tripped before the reconnect. The mutant that re-keyed the budget per socket failed at the predicted line, and that is what showed the test guards the hole.

## Non-vacuous gates (tondo crew-retention, 2026-10-10)
- T7 `crew-save-fits` (a 2 × 122-size layout sweep): with no visible sibling to measure against, the picker row's minimum clearance stayed `Infinity` and passed. The fix makes the probe `valid:false` unless the comparison set is non-empty and the button it guards has a box, and adds an `elementFromPoint` occlusion check at the scroll end. Sabotage, each with `styles.css` restored and `cmp`-identical: hiding New pie made the button row `INVALID` at 122 of 122 sizes (the picker row, with no sibling left, was invalid too); an invisible sheet over the scoreboard (every older assertion still held) gave "covered by #scoreboard" at 122 of 122. Green run prints `valid=122/122`.
- T8 `crew-card-fits`: the realistic fixture's names were too short to overflow, so a `white-space: nowrap` sabotage passed against it; a worst-case fixture (24-char crew name, 14-char member names) failed it at slack −184 px, 32 of 32 sizes.

## Positive controls and primary data
- arrows-game W6-07 (2026-09-19): "0/10 crash records survive" came from grepping a log sink registered only under `__DEV__` in a release build; the logcats held 0 `[telemetry]` lines of any kind.
- HALLOWEEN-01: R8 renames helper classes, so a dex string search sees only the manifest-kept class; a zero for the others is blind, not proof.
- geoguesser-app C1a (2026-09-16): a coverage check trusted the report's own `reconciled` flag and passed n=240 against a table needing 18,432; across 16 instances the rule became "attack every gate with synthetic input; recompute from primary data".
- tondo: a harness attached to a zombie Chrome produced a vacuous pass, "3/3 surviving with ZERO repaints".
