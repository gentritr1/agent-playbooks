---
name: rn-render-perf
description: Before dense or animated RN drawing, jank/fps, Skia/SkSL or gfxinfo.
---

# React Native rendering performance

arrows-game board (2026-09), geoguesser globe (2026-10-08); emulator numbers. Order of work:
1. Failure, device class, threshold (TEST-006).
2. Owner by per-frame traffic (EXPO-004): static dense → retained bounded owner (native 11.45 vs Skia 18.78 ms; one Svg, EXPO-005); a few numbers → UI-thread transform; per-pixel reprojection → GPU shader (0 vs 1–2 drops; ~9.9 MB lib, field guide §08).
3. Both arms in one APK, interleaved, vsync-counted (REND-005, TEST-003).
4. Readiness from the real trigger (REND-003); probe lines and QA trigger in the brief (CLAUDE.md §6).
5. Device: crash buffer, motion ON and OFF (ANDR-006, EXPO-001). Soak. Delete the loser.

### EXPO-004 · Fix dense or per-frame rendering by ownership, not by "go native"
- **Rule:** Cut per-item multiplicity, give static geometry one retained owner bounded to the viewport, and per frame send a few numbers (transform, shader uniform), never a commit or new geometry; per-frame reprojection goes to a GPU shader.
- **Kind:** heuristic — goal: no dropped frames in motion, p95 inside the gate on the densest scene; override: stronger case evidence, stated in the report; expires: 2027-01-06
- **Evidence:** arrows-game: first native display list 125.6 ms p95, retained native view 11.45 ms (gate 20); geoguesser: SVG `d` at ~46 KB per frame dropped 1–2 frames per spin, a Skia shader 0 → [dense-and-per-frame](evidence/dense-and-per-frame.md)
- **Confidence:** VERIFIED — API 31 and 36 emulators; no phone or iOS soak
- **Gate:** both arms in one APK, interleaved, judged on dropped vsyncs or p95 against a null (TEST-003), plus the work before motion starts, plus a same-process soak of the real interaction mix; a render-count probe prints commits during motion
- **Valid while:** `expo@54|57` `react-native@0.81|0.86` · host-GPU emulators · last_validated: 2026-10-08
- **Source:** EXPO-004

### REND-001 · Stop UI-thread writes before a Skia Canvas unmounts
- **Rule:** Stop a Canvas's frame callbacks and mappers on the UI thread, wait for an ack plus one frame, then unmount; read size from `SkiaViewApi.size(nativeId)`, never `onSize`.
- **Kind:** fact — the registry revives a dropped id with no view, `onSize` dereferences it unchecked, and `dispose()` is a no-op.
- **Evidence:** geoguesser: SIGSEGV in `setJsiProperty` ~200 ms after an unmount, 4,307 tests green; arrows-game patched the same registry in 2.6.2 → [skia-lifecycle](evidence/skia-lifecycle.md)
- **Confidence:** VERIFIED — device crash, path in source; the fix's device side is not
- **Gate:** the registry's test fake throws on writes to a dropped view; `logcat -b crash` stays empty after each unmount path (ANDR-006)
- **Valid while:** `@shopify/react-native-skia@2.2.12` `react-native-worklets@0.5` · last_validated: 2026-10-08
- **Source:** REND-001

### REND-003 · Readiness comes from the real trigger; nothing visible waits
- **Rule:** Measure a readiness deadline or a winner in the real context (cold start, full interaction mix), not a spike; warm optional GPU work at idle and play it at the first entrance after.
- **Kind:** heuristic — goal: no entrance stalls or silently skips; override: stronger case evidence, stated in the report; expires: 2027-01-06
- **Evidence:** geoguesser: spike ready in 15.9–43.2 ms, cold start 503–3,259 ms (8 of 8 skipped); arrows-game: a hybrid that won short runs failed a soak at ~50.7 ms p95 → [readiness](evidence/readiness.md)
- **Confidence:** VERIFIED — the gap, two projects; INFERRED — the warm entrance's frames are unmeasured
- **Gate:** the deadline cites a per-component cold-start probe timed from the trigger event, not a mount marker, n ≥ 5, on the target build
- **Valid while:** `ctx:react-native` · last_validated: 2026-10-08
- **Source:** REND-003

### REND-004 · Judge a layer change by its composite
- **Rule:** Judge every fade, hand-off or inserted layer by the composited pixels, not by the tree or each layer alone.
- **Kind:** invariant — why: tests and tree hashes pass while the screen composites wrong.
- **Evidence:** geoguesser: an overlay lit the night side ×1.47 while 4,225 tests passed; arrows-game: hide-and-show blanked 18 of 18 unmounts → [compositing](evidence/compositing.md)
- **Confidence:** VERIFIED — two firings
- **Gate:** a raster of the composite (rsvg-convert or capture), not a tree hash, shows: a fade moves only the top layer over an opaque one (else α·a + (1−α)²·b + α(1−α)·bg leaks, INFERRED); overlays are self-contained in their clip; hand-offs cover, never hide, with no blank frame
- **Valid while:** any layered renderer · last_validated: 2026-10-08
- **Source:** REND-004

### REND-005 · gfxinfo framestats: count vsyncs, not rows
- **Rule:** Group framestats rows by IntendedVsync, count drops from vsync gaps, window by the app's `logcat -v monotonic` lines; latency above a period or emulator deadline misses are not jank.
- **Kind:** fact — renders share a vsync, triple buffering exceeds a period, emulator latency modes flip deadline misses.
- **Evidence:** geoguesser: 86 rows for 43 vsyncs; jank 76 % legacy vs 0.43 %; 43 deadline misses in 0-drop runs; arrows-game: every frame "missed", no vsync skipped → [gfxinfo](evidence/gfxinfo.md)
- **Confidence:** VERIFIED — two projects; synthetic-dump test
- **Gate:** the parser passes a synthetic dump of known answers; vsyncs print beside window × refresh (TEST-004)
- **Valid while:** `ctx:android` · 60 Hz emulators · last_validated: 2026-10-08
- **Source:** REND-005

## Gates before you report done
Each rule's Gate; every frame claim also passes TEST-003 (null) and TEST-004 (reconciliation).

## Not covered / defer to
Reduced motion, Hermes, react-native-svg sizing: `expo-rn-apps`. Nulls and reconciliation: `testing-gates`. Pixel nulls, owner looks: `ui-motion-quality`. Motion craft: `animate-expo`.
