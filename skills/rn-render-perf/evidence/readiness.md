# Readiness deadlines: a spike measures the work, not the contention

**Source:** geoguesser-app `docs/engineering-lessons.md` L2 (2026-10-08); geoguesser-app `docs/plan/evidence/device-2026-10-07/bakeoff/1008-0732/skia-ready-*.txt`, `c/art4b-base-0830/summary.txt`, `c/art4b-spin-0908/summary.txt`, `c/art4b2-0952/summary.txt`, `c/art4b2-1025/summary.txt`, `c/art4b2-1212/summary.txt`, `c/art4b2-1308/summary.txt`; geoguesser-app memory `spike-ready-time-is-not-cold-start-ready-time.md`; arrows-game `docs/performance/field-guide.md` §04 ("realistic sequences change the winner"); arrows-game memory `polish-t6-handoff-and-gotchas.md` (2026-09-24), `w4-09-gallery-perf-and-capture-gotchas.md` (2026-09-25); arrows-game `docs/engineering-lessons.md` (W5-17, 2026-10-06); geoguesser-app `docs/handoff/drafts/ART-4b-brief.md` [R7ii].

## geoguesser-app, API 36 arm64 AVD, 2026-10-08
| Context | Same Skia prep (require, effect compile, mask fetch+decode, surface size, warm-up ticks) |
|---|---|
| Bake-off spike, app idle, inside a QA modal | ready in 15.9–43.2 ms (4 runs) |
| Cold start of the real home, from mount (0908, 8 cold starts) | late-ready 503, 1,802, 2,658, 2,171, 3,259, 2,781, 2,683, 2,515 ms: "0 spun, 8 skipped" against the brief's 200 ms, a deadline nobody had measured (it came from the fade length) |

- The base APK, with no spin at all, drew 30, 7 and 3 vsyncs of ~84, ~77 and ~53 expected in the entrance window of three cold starts (0830): start-up owns the JS and UI threads.
- A redesign that started the spin "late" when ready (0952 cold#3, ready at 488 ms) ran 11 UI-thread ticks of 31 expected, p95 = max = 350 ms.
- Final design: the hero never waits; Skia warms on an idle turn after the first frames; the spin plays at the first home entrance after warm-up. Device logs: cold starts log `skip why=notWarm` (4 of 5 in 1025, 3 of 3 in 1212, 3 of 3 in 1308) and warm-up lines of 196, 240, 1,880 and 2,710 ms.
- Not yet measured: the frames of that warm entrance on a device (the entrance deadline is still being set from a QA probe), so the design half of REND-003 is INFERRED.

## Time from the trigger event, not a mount marker
- arrows-game W5-17 (2026-10-06, `docs/engineering-lessons.md` "count a reveal's delay from the event, not from the mount"): the outline node mounted 93–262 ms after the clearing tap under load; a delay counted from the mount squeezed a 400 ms slot to ~250 ms. W4-09 (memory, 2026-09-25): a `useEffect` marker can land one frame late; take the mount frame from framestats.
- geoguesser ART-4b brief [R7ii]: "count from the first VISIBLE hero frame, including the warm-up draw".

## arrows-game (field guide, 2026-09-01)
- "Some hybrid effects won short interactions"; a static-Skia plus SVG-feedback hybrid then failed a multi-exit soak at ~50.7 ms p95. Interaction mix and lifecycle chose the winner, not the microbenchmark.
- POLISH-T6 (2026-09-24): the first overlay paint after launch was sensitive to new Skia draw types (a stroked closed triangle or a path-op union delayed it ~1 frame, 318 vs 334 ms, one heart run each). Measured with a relaunch-per-sample cold-tap harness, not a warm loop.
