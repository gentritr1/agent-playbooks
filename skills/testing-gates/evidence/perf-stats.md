# Performance statistics: nulls, replication, reconciliation, configuration

**Source:** `~/.claude/CLAUDE.md` §6 red flags; arrows-game memory `range-inside-range-criterion-invalid.md` (2026-09-25), `tap-forgiveness-and-verification-gaps.md` (2026-09-08), `art-skins-08-review.md` (2026-10-02), `w5-02-08-harness-gotchas.md` (2026-09-27); arrows-game `docs/engineering-lessons.md` (ART-SKINS-01/02 2026-09-30, "validate parser counts", W3-15 2026-10-06); arrows-game reports POLISH-T11 (2026-09-25), ART-SKINS-01/03, FINAL-FIX (2026-09-28); arrows-game `docs/performance/field-guide.md` load-gate note (2026-10-07); merge-kit memory `perf-gates-need-jitter-and-resolution-tolerance.md`, `ui-thread-sampling-needs-runonjs.md`; offbeat memory `offbeat-measurement-traps.md` (2026-10-02); geoguesser-app `docs/plan/evidence/device-2026-10-07/bakeoff/RESULT.md` (2026-10-08).

## Null spread and replication
- Range-inside-range: 8 vs 8 runs of the SAME build failed it on 4 of 5 metrics (W4-07 fix round, 2026-09-25).
- ART-SKINS-01: static recording +2.4034 ms vs an OFF null p95 spread of 0.0781 ms; a reviewer replicate (16 shuffled runs, 8 OFF / 8 ON) gave 0.24 → 2.45 ms medians with non-overlapping ranges. Permutation spec: 20,000 label permutations, plus-one correction.
- ART-SKINS-02: run order put the first 7 runs all OFF, confounding time with treatment; randomise within pairs.
- W5-02: a same-APK null reached p = 0.043 on one of 7 metrics; one flagged metric near p 0.03 is the instrument's false-positive level.
- merge-kit: a JS p95 of 16.97 ms with zero dropped frames was reported as "gate failed at 40 bodies" when the real cliff was ~100; allow for jitter and resolution.
- Tap forgiveness (2026-09-08): identical-APK exit phases swung 21.0 vs 36.1 ms, ~15 ms resolution; FINAL-FIX: the instrument resolved nothing below ~±25 ms at that n and load.

## Reconciliation
- merge-kit: a UI-thread sampler reported 1229 samples of ~1800 expected, then 0, then 1, each with a plausible p95.
- arrows-game 2026-09-30: a parser rejected every gfxinfo row because Android CSV lines end with a comma; after the fix 851 frames matched all 48 benchmark counts.
- geoguesser-app 2026-10-08 (globe bake-off): a framestats parser counted ~85 rows per 700 ms spin as frames, where the window held ~43 vsyncs (86 rows for 43 vsyncs in the corrected summary): a Modal and the activity share vsyncs. Rows not reconciling with window × refresh was the tell; the rewritten parser was first run on a synthetic dump with known answers (42 vsyncs in 56 rows, 2 missed, 2 deadline misses). Source: geoguesser-app `docs/plan/evidence/device-2026-10-07/bakeoff/RESULT.md`, memory `gfxinfo-rows-are-not-frames.md`. Rule detail: `rn-render-perf` REND-005.
- One clock per duration: geoguesser-app memory `device-and-web-qa-harness-traps.md` #5 (2026-09-30): the AVD's clock ran ~19.9 s behind the host's and drifted, so `host_stamp − app_stamp` silently corrupted two intermediate B1-3 results; take both ends from device time and print the offset. arrows-game W5-17 (`docs/engineering-lessons.md`, 2026-10-06): `dumpsys input` `eventTime` is CLOCK_MONOTONIC in ns while `logcat -v monotonic` prints seconds; every tap→handler delta was null until both were converted, so print the raw values next to the delta.
- W3-15 (2026-10-06): an overflow guard rejected 3/3 sessions; the split was 122 = 1 before + 48 inside + 73 after the window, because the history was read after slow dumps. Reading it first fixed 40 runs.
- offbeat: two overlapping probe loops recorded 288 frames where 151 were expected.
- POLISH-T11 formula: expected frames at 60 Hz = span / 16.67 + 1 per contiguous run (vsync gaps < 100 ms), + 1 per isolated frame.

## Configuration and control arm
- ART-SKINS-02/03: the PERF build lacked the zoomed-camera flag, so the "dense" level drew the flat 10 dp tier; players see ~29.39 dp full detail, where preparation was 45.9 ms median vs a 16 ms budget.
- ART-SKINS-08: Classic OFF measured 31–48 ms vs 5–9 ms in the previous round (11.8 GB swap, load 9–25); every treatment number from that round was unusable.
- Tap forgiveness: the unchanged HEAD measured 3× worse than its 2026-09-01 record on a loaded Mac; only paired differences counted.
- The field guide (2026-10-07) adds a load gate before a series and a load record before and after every arm.

## Early stopping replayed and rejected (arrows-game 2026-10-07)
**Source:** arrows-game `docs/process/speed-experiments-2026-10-07.md` (E2, rule E2-R1 pre-registered and committed before any outcome was opened). Replayed on 87 archived A/B(/null) series, 1,894 runs: it would have saved 590 runs (31.2 %), but 15 of 87 series flipped verdict (7 without counting stops on series the report called inconclusive), and with shuffled labels the sequential rule claimed a false effect more often than one fixed-n look in 48 of 87 series. Retired as TEST-902; TEST-003's gate now requires the planned n.
