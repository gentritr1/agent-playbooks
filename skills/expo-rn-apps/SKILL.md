---
name: expo-rn-apps
description: Use before changing an Expo or React Native app's animation, reduced motion, EXPO_PUBLIC env flags, Hermes performance, dense rendering, react-native-svg or Android text fitting, or before claiming such a change works.
---

# Expo / React Native apps

Measured on our Expo apps. Gates say what must be true when you finish; the evidence says why. A rule marked VERSION-DIFFERS by `tools/check-applicability.py` is unverified in your project.

### EXPO-001 · Every Reanimated animation declares its reduced-motion behaviour
- **Rule:** Give each `withTiming`/`withSpring`/`entering` an explicit `reduceMotion`, and give motion that carries information a static stand-in.
- **Kind:** invariant — why: with the OS setting on, default animations jump to their end state and players lose the feedback.
- **Evidence:** arrows-game 2026-09-09: blocker flash, bump and paid hint drew nothing; geoguesser 2026-09-16: delayed `entering` left a view blank on 4 of 5 installs → [reduced-motion](evidence/reduced-motion.md)
- **Confidence:** VERIFIED
- **Gate:** a source-audit test fails on any timing call without `reduceMotion`, and a device capture after `transition_animation_scale 0` + relaunch shows the static state
- **Valid while:** `react-native-reanimated@4.5` · Android API 31 emulator · last_validated: 2026-10-04
- **Source:** EXPO-001

### EXPO-002 · Prove an EXPO_PUBLIC value from the built bundle
- **Rule:** After changing an `EXPO_PUBLIC_*` value, rebuild without cached bundles and prove the value in the artifact.
- **Kind:** fact — values are inlined at bundle time; Metro and Gradle reuse a stale bundle and still report success.
- **Evidence:** geoguesser 2026-09-16: bundle task `UP-TO-DATE`, store artifact carried the QA bundle (same sha256); arrows-game 2026-09-17: positive control read 0 until `--clear` → [env-inlining](evidence/env-inlining.md)
- **Confidence:** VERIFIED
- **Gate:** byte count in the built bundle: new value ≥1, old value 0, a known-present control string ≥1 (UTF-8 and UTF-16LE)
- **Valid while:** `expo@57` · Gradle JS bundle task · last_validated: 2026-09-17
- **Source:** EXPO-002

### EXPO-003 · Size JS hot paths on Hermes, not node
- **Rule:** Time JS work from a release Hermes bundle on the target runtime before sizing a budget.
- **Kind:** fact — Hermes has no JIT; V8 in node is several times faster and allocates far less.
- **Evidence:** arrows-game 2026-09-25: ~5× slower, ~30× more allocation than V8; merge-kit: physics 11× cheaper under node → [hermes-and-rendering](evidence/hermes-and-rendering.md)
- **Confidence:** VERIFIED
- **Gate:** the budget cites a release-build log timing on emulator or device, with n
- **Valid while:** `react-native@0.86` Hermes · last_validated: 2026-09-25
- **Source:** EXPO-003

### EXPO-004 · Fix dense rendering by ownership, not by "go native"
- **Rule:** Remove per-item multiplicity first, then give static geometry one retained, bounded owner.
- **Kind:** heuristic — goal: active-frame p95 inside the gate on the densest scene; override: stronger case evidence, stated in the report; expires: 2026-11-30
- **Evidence:** arrows-game 2026-09-01: ~750 SVG nodes; first native display list 125.6 ms p95, retained native view 11.45 ms (gate 20 ms), emulator only → [hermes-and-rendering](evidence/hermes-and-rendering.md)
- **Confidence:** VERIFIED — API 31 emulator; no phone or iOS soak
- **Gate:** release soak passes the frame gates against a same-build null (TEST-003)
- **Valid while:** `expo@57` `react-native@0.86` · API 31 emulator, host GPU · last_validated: 2026-09-01
- **Source:** EXPO-004

### EXPO-005 · One Svg, sized by its parent
- **Rule:** Draw many shapes as Paths in one `Svg`, and size it with a `View` plus `width="100%"`.
- **Kind:** fact — Android `SvgView` rasterises each Svg into its own bitmap and `parseInt`s numeric sizes.
- **Evidence:** arrows-game 2026-09-25: gallery mount frame 69 → 41 ms (n=24); 2026-10-06: `width={80.5}` laid out at 80 → [hermes-and-rendering](evidence/hermes-and-rendering.md)
- **Confidence:** VERIFIED
- **Gate:** a layout test pins the fractional size; first-frame timing against the old layout
- **Valid while:** `react-native-svg@15.15` · last_validated: 2026-10-06
- **Source:** EXPO-005

### EXPO-006 · Android shrinks text that already fits
- **Rule:** Enable `adjustsFontSizeToFit` only on text measured to overflow.
- **Kind:** fact — Android re-runs the fit on a pixel-snapped height and shrinks text that fits.
- **Evidence:** arrows-game 2026-10-06: every one-line title ~8 % smaller at 480 dpi, unchanged at 560 dpi → [hermes-and-rendering](evidence/hermes-and-rendering.md)
- **Confidence:** VERIFIED
- **Gate:** pixel diff of a fitting case at 480 and 560 dpi is 0 px
- **Valid while:** `react-native@0.86` · last_validated: 2026-10-06
- **Source:** EXPO-006

## Gates before you report done
- Reduced motion: EXPO-001 audit test plus the device capture.
- Env flags: EXPO-002 bundle counts, with the positive control.
- Perf: a release build on the target runtime, against a null (TEST-003).
- Layout or event edits: open the screen on a device (UI-002).

## Anti-patterns we measured
- Event values read inside a `setState` updater crashed every round on device after 521 green tests (UI-002).
- Disabling feedback to win frames: diagnostics are not product decisions ([field guide extract](evidence/hermes-and-rendering.md)).

## Not covered / defer to
Upgrades, modules, routing and EAS: `expo:*` skills. Motion design: `animate-expo`. General RN patterns: `react-native-skills`.
