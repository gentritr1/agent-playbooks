# Hermes cost, dense rendering, react-native-svg, Android text fit

**Source:** arrows-game `docs/performance/field-guide.md` (2026-09-01, the feedback-ablation note); arrows-game memory `w4-07-hermes-fold-and-boot-trace.md` (2026-09-25), `w4-09-gallery-perf-and-capture-gotchas.md` (2026-09-25); arrows-game `docs/engineering-lessons.md` (W5-13 vector art, HEADER-FIT, both 2026-10-06); merge-kit memory `v02-spike-outcome-matter-js-fails-120.md` (2026-07-25).

## Hermes vs node
- arrows-game W4-07, API 31 emulator, release bundle: `shapeNameForLevel` ~26 µs and ~6.6 KB garbage per level on Hermes; V8 ~5× cheaper and ~30× less allocation.
- merge-kit: physics linear at 0.181 ms per body per 60 Hz step on Hermes; the same scenario under node/V8 measured 1.81 ms/step, which the note calls 11× cheaper (simulator; the note calls it inadmissible for a formal pass).

## Dense board
Moved with EXPO-004 to `rn-render-perf` ([dense-and-per-frame](../../rn-render-perf/evidence/dense-and-per-frame.md)) in v0.5.0. Kept here for the anti-pattern: the field guide records that disabling feedback is a diagnostic, not a product decision (EXPO-902 in `retired/`).

## react-native-svg (Android)
- `SvgView` rasterises each `Svg` into its own bitmap: one Svg with translated Paths cut the gallery mount frame 69 → 41 ms (n=24). Snap Path origins like Yoga at fractional densities (14k px differed at 3.5 until snapped).
- `<Svg width={80.5}>` laid out at 80 × 80: numeric sizes go through `parseInt`, which wins over `style`. Correction: size a `View`, give the Svg `width="100%" height="100%"`.

## Android `adjustsFontSizeToFit`
- HEADER-FIT 2026-10-06: with the prop on permanently, every one-line title painted ~8 % smaller at 360 dp / 480 dpi (48 px vs 52 px) although it fitted; unchanged at 560 dpi. Cause read from RN 0.86 source (`ReactTextView.onDraw` re-fits against the pixel-snapped height), not instrumented. Fix: enable the shrink only after `onTextLayout` reports two lines; one-line headers then pixel-identical at three geometries.
