# gfxinfo framestats: vsyncs, not rows; drops, not latency

**Source:** geoguesser-app `docs/plan/evidence/device-2026-10-07/scripts/framestats.py`, `bakeoff/RESULT.md` ("Instrument notes"), `bakeoff/1008-0732/summary.txt`, raw dumps `bakeoff/1008-0635/*.txt` re-scored with `framestats.py` on 2026-10-08; geoguesser-app memory `gfxinfo-rows-are-not-frames.md`; geoguesser-app `docs/engineering-lessons.md` L5; arrows-game memory `w4-09-gallery-perf-and-capture-gotchas.md` (2026-09-25); arrows-game `docs/engineering-lessons.md` ("Performance evidence: validate parser counts against raw rows").

## Rows are renders (geoguesser-app, 2026-10-08)
- The first parser counted every `---PROFILEDATA---` row as a frame: ~85 per 700 ms spin. The windowed summary shows 86 rows for 43 vsyncs; a whole 2 s dump had 166 rows, 46 of them at a 0.0 ms IntendedVsync delta (a Modal window and the activity, or a TextureView update and a traversal, share a vsync).
- It also called a frame janky when FrameCompleted − IntendedVsync exceeded one period: ~100 % in both arms and at idle. Android's own summary said 0.43 % janky against the legacy rule's 76 %; triple buffering makes latency above one period normal.
- The reconciliation caught it: rows did not match window × refresh (TEST-004).

## Corrected instrument (framestats.py)
- Group rows by IntendedVsync (drop rows with Flags ≠ 0); per vsync keep the latest FrameCompleted and its FrameDeadline.
- Dropped frames = gaps between consecutive vsyncs larger than 1.5 periods, counted in periods (meaningful only while something animates every frame).
- Deadline misses = vsyncs whose FrameCompleted > FrameDeadline; GPU time = GpuCompleted − IssueDrawCommandsStart.
- Window = the app's own start and end log lines read with `logcat -v monotonic` (same clock as gfxinfo, checked against `/proc/uptime`).
- Attacked first with a synthetic dump of known answers: 42 vsyncs in 56 rows, 2 missed, 2 deadline misses, GPU 3.00 ms.

## Deadline misses and latency do not measure drops on the emulator
- geoguesser 1008-0732, Skia arm, 0 dropped frames in all 4 runs: deadline misses 43, 1, 1, 43, tracking the emulator's latency mode (p50 34.1 / 25.7 / 25.9 / 34.2 ms). The SVG arm, which did drop frames, showed 1–2 deadline misses per spin. Re-scoring the earlier 1008-0635 dumps gave the same split over whole 2 s dumps (Skia 41–47, SVG 3–4).
- RESULT.md first said the flip happened "in BOTH arms"; re-scoring showed it in the Skia arm only, and RESULT.md now reads "Skia arm per spin: 43, 1, 1, 43; the SVG arm stayed at 1-4; corrected 2026-10-08 by the playbook review". The metric is anti-correlated with drops in this bake-off and does not discriminate.
- arrows-game 2026-09-25 (API 31 emulator): whole windows with DequeueBufferDuration ~14 ms, frames ending ~20 ms after vsync, every frame "missed" and no vsync skipped. Report app work beside duration; never quote "missed" alone.
- arrows-game 2026-09-30: a parser rejected every gfxinfo row because Android's CSV lines end with a comma (TEST-004 evidence).
