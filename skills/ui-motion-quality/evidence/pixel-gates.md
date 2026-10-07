# Pixel and contrast gates

**Source:** arrows-game memory `art-skins-07-review.md`, `art-skins-08-review.md` (2026-10-02), `w5-art-batch-gotchas.md` (2026-09-27), `detector-needs-positive-control.md` (2026-09-19); arrows-game `docs/engineering-lessons.md` (ART07 LOD-proof correction, ART08 exact OFF, "A contract rule can be wrong", K4 alpha precondition, HALLOWEEN-01); arrows-game reports P-02 (2026-09-19), W0-06 (2026-09-16), W7-09 (2026-10-06); `docs/skins/README.md` K4.

## Null controls
- ART07 (2026-10-02): an exact-pixel OFF gate failed with 316 px (mostly one edge off by 1/255) comparing installs of two different APKs with no reinstall control. ART08 ran base/base and base/OFF: 0 changed pixels, max delta 0; ART07's base capture was the odd one.
- W5-16: two launches of the same board differed by 4 anti-aliased pixels (RGB-sum ≤ 43); a whole-screen diff needs a tolerance taken from such a null.
- P-02: an A ∪ B floor of 0 px let a scale-0 blocked tap pass on 6 px of redraw antialiasing; the floor became 28 px with a non-rendering control and a held-out cell.

## Positive controls
- W5 (2026-09-27): a tolerance of max channel > 24 was blind to effects under ~10 % opacity (grain 0.08 = max delta 18).
- ART07 (2026-10-02): a supplemental pixel helper drew a blank tier, so its equivalence claim was vacuous; the corrected helper requires non-background pixels in every comparison (269,201,210 samples, 357 displaced-path controls rejected).
- W7-09: a Chrome-equivalence gate rejected PERF-build captures at 1,645 changed px, all inside the hint button, against a 28 px floor.

## Contrast
- 2026-10-01: the skin contract required the body fill to be ≥ 3:1; meeting it darkened a dough colour to chocolate brown. Legibility is carried by the outline; the gate moved to the rim (Cinnamon 5.210:1 / 3.584:1, Sherbet 5.099:1 / 3.662:1 on light/dark).
- A hex ratio assumes an opaque colour; translucent outlines need the composite over each real background (17 weakened-alpha controls).
- W0-06: contrast maths pinned to WCAG references, `#767676` = 4.54:1 and `composite('#000',0.45,'#FFF')` = `#8C8C8C`; several rows sit at 3.00–3.01 and 4.50–4.51, so display rendering is not modelled.
- HALLOWEEN-01 (2026-10-04): an owner-approved concept tint failed the missed-mark row at 2.992:1; approval of a concept does not replace the audit.
