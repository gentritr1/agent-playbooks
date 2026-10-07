# Timing from screen recordings

**Source:** arrows-game `docs/engineering-lessons.md` (ART-SKINS-02 "Motion evidence rule" 2026-09-30; HALLOWEEN-PLUS 2026-10-06/07); arrows-game memory `capture-harness-gotchas-t5.md` (2026-09-24/26), `w2-08-06-10-capture-gotchas.md`, `w2-05-capture-gotchas.md`; geoguesser-app `docs/handoff/CODEX-HANDOFF.md` §6 ruling R54; arrows-game report W0-07 (2026-09-17).

- `screenrecord --time-limit 10` did not guarantee a 10-second file or 60 Hz: native captures had 83 and 50 frames with median gaps 66.62 and 74.88 ms, too sparse for a 90 ± 17 ms press timing (2026-09-30).
- Loaded host (load ~10): one session produced 17 frames in 20.9 s (2026-09-26).
- Loaded host (load 15–48): `adb shell screenrecord` fell back from 1440×3120 to 720×1280; `adb emu screenrecord` recorded full resolution at ~6 distinct frames/s (2026-10-07).
- `ffmpeg -ss t` returns the first frame after t, which showed a blank hand-off frame as "+150 ms"; select the last pts ≤ t. `-frame_pts 1` silently overwrites frames that share a rounded pts.
- geoguesser-app R54: the emulator's `screenrecord` encodes 8–70 % of frames; compute encoded frames / (duration × 60) with ffprobe and reject clips under 90 % before any frame-timing analysis.
- W0-07: SurfaceFlinger `--latency` served as an independent clock; in all 12 captures every flash frame matched a SurfaceFlinger present, mean |error| 0.08–0.32 ms.
