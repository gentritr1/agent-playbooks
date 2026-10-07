# Persisted-schema changes and wipe risk

**Source:** `~/.claude/CLAUDE.md` §3; planet-drop memory `save-additive-schema-safety.md` (recurred 2026-07-13), `reviewing-codex-output.md`; geoguesser-app memory `playerstore-wipes-profile-on-slow-read.md` (2026-09-09); arrows-game `docs/engineering-lessons.md` ("Runtime skins: preserve gate, save ownership and configuration across selection", ART-SKINS-06 2026-10-01); lucky-shelf memory index (catalog-wipe, third firing); wordle memory `daily-pool-immutability.md`.

- planet-drop: a checksum checked before the schema version wiped saves when an additive field was introduced. It recurred 2026-07-13: a delegate added `settings.reduceMotion` to the save model without bumping the schema version, so every existing save would checksum-mismatch on the next load and be wiped. A test had exercised the migration helper in isolation while the real wipe happened in `Load()`.
- geoguesser-app 2026-09-09: a slow cold read's timeout handler marked the store ready while it still held defaults, and the profile was overwritten. Fixed (two commits) and pinned by a test; lesson: "When adding a background retry, never reuse a timeout that exists for UI responsiveness."
- arrows-game ART-SKINS-06 (2026-10-01): a new saved preference was added as one additive key behind a flag; Jest verified every existing key round-trips unchanged ON/OFF, failed hydration cannot write, and a downgrade ignores and retains the saved id. Unknown ids resolve to the default without repair writes; ids are never reused.
- lucky-shelf: a catalogue wipe, third firing of the same failure class (per its memory index).
- wordle: the first 62 daily words are pinned by a SHA test so a content change cannot silently re-deal shipped days.
