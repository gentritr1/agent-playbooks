# Dense and per-frame rendering: who owns the work, and what crosses the boundary each frame

**Source:** arrows-game `docs/performance/field-guide.md` (2026-09-01: §02 production evidence, §04 assumptions corrected, §06 experiment ledger, §08 native modules, Recipe A); arrows-game `docs/perf-mask-rebuild-2026-09-17.md` (W6-01); arrows-game memory `heart-emoji-and-board-perf.md` (2026-07-19) and `perf-architecture-and-evidence.md`; geoguesser-app `docs/plan/evidence/device-2026-10-07/bakeoff/RESULT.md`, `bakeoff/1008-0732/summary.txt`, `svg-ready-*.txt`, `skia-ready-*.txt` (2026-10-08); geoguesser-app `docs/engineering-lessons.md` L1.

## Dense static board (arrows-game, release soak, API 31 emulator, host GPU, 20 levels, 2,247 removals)
| Renderer | Active frame p95 | Decision |
|---|---|---|
| SVG, ~750 host nodes (250 arrows) | ~124.7 ms | superseded |
| Two compound SVG paths | ~110.6 ms, still 100 % jank | superseded |
| Early native display list (large transformed child) | ~125.6 ms | rejected |
| Skia survivor paths | 18.78 ms | baseline |
| Retained native board view | 11.45 ms (p99 13.45, jank 0.19 %) | accepted; gate p95 ≤ 20 ms |
| Empty scene floor | 9.79 ms | diagnostic only |

- The guide's verdict: the win came from a bounded, retained, local, event-driven owner, not from "native" itself. "Cross runtime boundaries with facts, not frames": geometry once per mission, a bounded visibility change per exit, one tap coordinate back.
- Boundary cost measured (W6-01, 2026-09-17, 250 arrows): the O(n) mask build took 0.0416 ms median in JS and 0.1352 ms median in the native setter, while frames that carried a React commit cost 8–9 ms median and frames without one 0.14 ms. The commit, not the O(n) work, was the cost.
- Memoising the leaf (2026-07-19): one tap re-rendered 273 arrow components before `React.memo`, 1 after. The field guide records that the largest cost stayed in host nodes, surfaces and draw work after React churn fell: memo is necessary, not sufficient.
- Bounded, or it gets worse: a native exit overlay that redrew the root measured ~20.4 ms p95 and 27.5 % jank (rejected); a forced compositor layer regressed the SVG path.
- Backing surfaces: a 1560×1560 logical board at density 3.5 is 5460×5460 px × 4 B = 119,246,400 bytes; bounding the drawing surface to the viewport stopped the crash (Recipe A: logical × density per side × 4 bytes).
- No physical-device or iOS soak exists for these numbers.

## Soak and render counts (EXPO-004's gate)
- A pre-native 50-level soak passed its frame gate but grew 26.57 MB in the leak-sensitive window; a single-mission microbenchmark could not see it. A static-Skia plus SVG-feedback hybrid that won short interactions failed a multi-exit soak at ~50.7 ms p95 (field guide §02 "Memory needed a lifecycle test", §04).
- Render counts (memory `heart-emoji-and-board-perf.md`, 2026-07-19): measure with a per-render `console.count`, not just gfxinfo; a SwiftShader emulator pins jank at ~95 % regardless, so the render-count delta (273 → 1 per tap) is the hardware-independent signal.

## Ledger negatives an agent might retry (field guide §06, 2026-09-01; "rejected" means for this workload)
- A forced compositor layer regressed the SVG path and added texture and compositor cost.
- Explicit Hermes GC at mission boundaries worsened the memory slope ~936 → 989 KB per level (EXPO-903).
- A recorded SkPicture raised first-level PSS ~13.1 MB and did not solve the soak.
- Lower allocation is not lower latency: shared survivor compounds measured 20.57 ms p95 and 20.94 % jank, failing the frame gate.
- Gesture write coalescing reduced vertical-pan frame delivery and changed input quality: an optimisation that drops input is a regression.

## Price of a native owner (field guide §08 "Price of admission")
Two platform implementations, dev/release builds instead of Expo Go, lifecycle testing, bridge validation, upgrade maintenance and a web fallback. Good candidates: high-frequency or latency-sensitive work, stable data, a direct platform primitive, a tiny API, measured cost, clear lifecycle.

## Per-frame geometry reprojection (geoguesser-app, 2026-10-08)
A 700 ms spin of a 448 dp orthographic globe (land, gores, graticule, night caps). Both arms in one QA APK, interleaved svg, skia, skia, svg, svg, skia, skia, svg; host load 5.2–6.6; API 36 arm64 AVD at 60 Hz; animator scales forced to 1. Instrument: `framestats.py` (vsync grouping, see [gfxinfo](gfxinfo.md)).

| Per spin, 4 runs per arm | SVG (`react-native-svg`, `useAnimatedProps` on `d`) | Skia (SkSL runtime shader) |
|---|---|---|
| Vsyncs drawn / expected | 44/45, 41/43, 44/45, 42/43 | 43/43 ×4 |
| Dropped frames (vsync gaps) | 1, 2, 1, 1 | 0, 0, 0, 0 |
| Max frame latency | 50.6–68.4 ms | 29.9–37.5 ms |
| Work before the spin can start | 42 precomputed path strings of ~44–47 K chars each, 1,070.7–1,161.9 ms of Hermes time per run (summed from the log) | ready in 15.9–43.2 ms |

- Cause: the SVG arm must regenerate each frame's path text on JS and RNSVG re-parses ~46 KB per frame; the shader inverse-projects per pixel on the GPU, so two floats change per frame.
- The drop ranges do not overlap and the result held in all 4 runs per arm. Emulator only; a phone GPU was not measured in the bake-off.
- Price of the shader route, as the lessons file L1 states it (not re-measured here): `librnskia.so` 9.9 MB installed, ~2.9–4.1 MB download; required lazily, so start-up with the flag OFF is untouched.
