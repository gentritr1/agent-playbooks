---
name: ui-motion-quality
description: Use before shipping or reviewing any visual, layout, motion or feel change, writing a pixel, contrast or screenshot gate, recording timing from captures, or asking the owner to accept a look.
---

# UI and motion quality gates

Taste is the owner's call; these rules make the evidence he judges honest. Visual design itself is out of scope.

### UI-001 · The owner accepts looks from a capture; the flag stays off until then
- **Rule:** Ship visual or feel changes behind a default-OFF flag until the owner accepts a named capture.
- **Kind:** invariant — why: tests cannot see taste, and the owner's words have meant something other than the literal reading.
- **Evidence:** arrows-game 2026-09-16 ruling; 2026-10-01: "not straight" meant misaligned accents, not slope; 2026-10-02: skins approved only after phone test builds → [acceptance](evidence/acceptance.md)
- **Confidence:** VERIFIED
- **Gate:** the report links the capture the owner accepted and quotes his yes; code default is OFF until that line exists
- **Valid while:** owner-run projects · last_validated: 2026-10-06
- **Source:** UI-001

### UI-002 · Layout, measurement and event edits close on the real screen
- **Rule:** Close a layout, measurement or input-path change only after opening that screen on a device or simulator and exercising each affected control.
- **Kind:** invariant — why: every headless check has passed while the screen was broken.
- **Evidence:** geoguesser 2026-09-30: event read inside a `setState` updater crashed every round after 521 green tests; arrows-game 2026-09-26: a wrapper ate taps while bounds checks passed → [headless-blind](evidence/headless-blind.md)
- **Confidence:** VERIFIED
- **Gate:** a device or simulator capture of the screen plus a logged result for each tapped control
- **Valid while:** `ctx:react-native` · last_validated: 2026-10-06
- **Source:** UI-002

### UI-003 · A pixel gate needs a null and a positive control
- **Rule:** Judge a pixel diff only against a same-build reinstall null and a positive control that changes the target pixels.
- **Kind:** invariant — why: without the null, noise fails a build; without the positive control, a blind detector passes one.
- **Evidence:** arrows-game 2026-10-02: a 316-px OFF failure vanished under a reinstall null (0 px); 2026-09-27: tolerance 24 was blind to effects under ~10 % opacity → [pixel-gates](evidence/pixel-gates.md)
- **Confidence:** VERIFIED
- **Gate:** the report prints null diff, positive-control diff and the tolerance derived from the null
- **Valid while:** any capture pipeline · last_validated: 2026-10-06
- **Source:** UI-003

### UI-004 · Contrast is measured on what carries legibility
- **Rule:** Apply contrast gates to the element that carries legibility, over the actual composited background.
- **Kind:** invariant — why: a gate on the wrong element ruined the art; an opaque hex ratio misreports translucent colours.
- **Evidence:** arrows-game 2026-10-01: a fill-contrast rule darkened a skin to brown; the outline carries legibility (rims 5.210:1 / 3.584:1) → [pixel-gates](evidence/pixel-gates.md)
- **Confidence:** VERIFIED
- **Gate:** the contrast test reproduces a WCAG reference pair (`#767676` on white = 4.54:1) and audits the composited colours
- **Valid while:** WCAG 2.x ratios · last_validated: 2026-10-04
- **Source:** UI-004

### UI-005 · Timing from recordings states its frame density
- **Rule:** Report frame count and gaps beside every timing read from a screen recording, and choose frames by presentation timestamp.
- **Kind:** fact — emulator `screenrecord` is variable-rate and drops frames under load; `ffmpeg -ss t` returns the first frame after t.
- **Evidence:** arrows-game 2026-09-30: 83/50 frames, median gaps 66.6/74.9 ms; geoguesser: 8–70 % of frames encoded → [timing](evidence/timing.md)
- **Confidence:** VERIFIED
- **Gate:** each clip's measured frame density ≥ 90 % of expected, or the timing is UNVERIFIED
- **Valid while:** `ctx:android` · emulator `screenrecord` · last_validated: 2026-10-07
- **Source:** UI-005

### UI-006 · Visual targets are absolute and judged at real and zoomed scale
- **Rule:** Specify visual targets as absolute sizes or looks, and show the owner both real-size and zoomed crops.
- **Kind:** invariant — why: multipliers on small constants ship invisible changes; some defects only show when zoomed.
- **Evidence:** planet-drop: "2.5× of nothing was still nothing"; arrows-game 2026-10-06: corner scallops invisible at board scale, obvious at 4× → [acceptance](evidence/acceptance.md)
- **Confidence:** VERIFIED
- **Gate:** the brief lists absolute targets; the report holds a 1× and a ≥4× crop
- **Valid while:** owner-run projects · last_validated: 2026-10-06
- **Source:** UI-006

### UI-007 · Responsive checks sweep the band
- **Rule:** Sweep widths across the whole range a layout supports instead of sampling a few breakpoints.
- **Kind:** heuristic — goal: no overlap at any common viewport; override: stronger case evidence, stated in the report; expires: 2026-12-31
- **Evidence:** tondo: samples green, sweep found 1366×768 at −2.5 px; form-studio: a row broke at 900–1240 px → [headless-blind](evidence/headless-blind.md)
- **Confidence:** VERIFIED
- **Gate:** a sweep in ≤ 40 px steps reports the minimum clearance and where its sign flips
- **Valid while:** `ctx:web` · last_validated: 2026-10-02
- **Source:** UI-007

## Gates before you report done
Owner capture and flag (001); device run of the screen (002); null + positive control (003); contrast reference pair (004); frame density (005).

## Not covered / defer to
Design and motion craft: `emil-design-eng`, `ui-ux-pro-max`, `animate`, `animate-expo`, `apple-design`. Reduced-motion code: EXPO-001.
