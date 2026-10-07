# Owner acceptance and absolute visual targets

**Source:** `~/.claude/CLAUDE.md` §2 and §5; arrows-game memory `owner-rulings-next-level-2026-09-16.md`, `art-skins-08-review.md` (2026-10-02); arrows-game `docs/engineering-lessons.md` ("Sherbet owner correction" 2026-10-01; "Rounding a cell staircase" W5-17 2026-10-06; Workflow Studio iteration 05 owner correction 2026-10-02); arrows-game reports W2-10/W2-11 (2026-09-26/10-06); planet-drop memory `visual-calibration-briefs-lesson.md` (2026-07-03).

- Owner ruling 2026-09-16 (arrows-game): every new player-visible feature ships behind a flag defaulted OFF until the owner accepts it from a screenshot.
- 2026-10-01: the owner's "not straight" feedback pointed at accents that were mathematically straight but shifted .065 cell off the head axis; narrowing the correction to one skin, or to line slope, would have missed it.
- 2026-10-02: launch skins were APPROVED only after phone test builds (vc11/vc12), merged behind a default-OFF flag.
- Workflow Studio iteration 05: repeated small polish passes kept a structure the owner had rejected as generic; component tests could not verify the taste requirement.
- W2-10/W2-11: measured motion legibility (lunge 4.1 / 15.0 / 2.2 / 14.2 pt) went to the owner; he ruled 2.2 pt does not read, which set a 4 pt floor.
- W5-17 (2026-10-06): per-corner fillets on a 1-cell staircase made scallops "near invisible at board scale and obvious at 4×"; the coordinator review of the zoomed preview rejected them.
- planet-drop 2026-07-03: a brief specified relative multipliers ("0.022 → 0.055", "alpha ×1.5") on values already near-invisible, "so 2.5× of nothing was still nothing"; the fix specifies proportions of a reference dimension.
