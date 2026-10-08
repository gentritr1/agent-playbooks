# Compositing: a layer change is right only if the composite is

**Source:** geoguesser-app commit `0dcc236` (fix(art-4a): fix round 1, 2026-10-08) and memory `overlay-redraws-break-when-a-layer-is-inserted.md`; geoguesser-app `docs/engineering-lessons.md` L7; arrows-game memory `polish-t6-handoff-and-gotchas.md` (POLISH-T6, 2026-09-24).

## An overlay that redraws a base layer (geoguesser-app ART-4a, 2026-10-08)
- The reward overlay re-painted a copy of the coast above the globe. ART-4a inserted night caps between the globe's coast and the overlay; the copy then painted undarkened coasts over the whole night side: ×1.47 coast luminance for the whole post-daily visit, and the slice darkened twice.
- 4,225 tests and 68 re-pinned tree hashes passed: they proved the tree diff, not what it composites to.
- Fix: everything the overlay draws sits in one group clipped to its slice, in the base layer's own order. rsvg raster check of the recorded trees: 11,041 px off (worst 143/255) before, 0 px off (worst 1/255) after.

## Hand-off between two unordered pipelines (arrows-game POLISH-T6, 2026-09-24)
- A retained native board view (Fabric mount, then a redraw one frame later) and a Skia overlay (a UI-runtime picture) have no ordering. Hiding an arrow in one and showing it in the other in one React commit blanked a frame on 18 of 18 unmounts with reduced motion and 9 of 18 with motion on.
- Fix: the native view never hides the shaking arrow; Skia draws a background-coloured cover under the moving copy; the mark is handed back to native at 170 ms.

## Crossfading two layers (math, INFERRED, not measured)
Layer a at α over an opaque under-layer b faded to 1 − α, over the background: α·a + (1−α)²·b + α(1−α)·bg, so the background leaks α(1−α), 25 % at α = ½ (re-derived by the v0.5.0 review). Holding the under-layer at 1 and fading only the top gives α·a + (1 − α)·b, no leak. Raised by the ART-4b brief review; the device look awaits owner sign-off.

## The three techniques REND-004's gate checks
Fade only the top layer over an opaque one; keep an overlay that redraws a base layer self-contained inside its clip, in the base layer's order; hand off between unordered pipelines by covering, never by hide-and-show in one commit.
