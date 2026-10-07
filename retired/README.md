# Retired rules

A rule lands here when evidence disproves it, a better rule replaces it, or the eval harness shows it does not help. Its id is never reused: `tools/lint-playbooks.py` fails if an active rule carries a retired id. To bring an idea back, open a new rule with a new id, cite the new evidence, and say in `CHANGELOG.md` why the retirement reason no longer holds.

Each entry: retired id, date, reason, the evidence that retired it, and what would reopen it.

## TEST-901 · "Every treatment run inside the control's range" as a perf gate
**Retired id:** TEST-901
- **Retired:** 2026-09-25
- **Reason:** identical builds fail it: 8 vs 8 runs of the same APK failed on 4 of 5 metrics (chance ~23 % per metric at n=8).
- **Evidence:** arrows-game memory `range-inside-range-criterion-invalid.md` (W4-07 fix round).
- **Replaced by:** TEST-003.
- **Reopen only if:** never as a gate; ranges stay useful as a replication check beside a null spread.

## PROC-901 · Use a code knowledge graph (Graphify) as project memory
**Retired id:** PROC-901
- **Retired:** 2026-10-07
- **Reason:** 3 of 12 real questions fully correct; 4 of 4 stale answers after edits, exit 0, no warning; realistic token cost 7.5 % higher than grep plus read.
- **Evidence:** arrows-game `docs/process/graphify-trial-2026-10-07.md`.
- **Replaced by:** PROC-003 for any cache that is used.
- **Reopen only if:** a ledger shows "who calls X" questions dominate re-read cost, and a new version checks freshness at query time and indexes literal values.

## PROC-902 · "Builds are the main time sink; optimise them first"
**Retired id:** PROC-902
- **Retired:** 2026-10-07
- **Reason:** measured at 6.2 % of 101.3 active helper hours; model time was 34 % and perf series 23 %.
- **Evidence:** arrows-game `docs/process/speed-audit-2026-10-07.md`.
- **Replaced by:** PROC-002.
- **Reopen only if:** a newer ledger shows builds above 15 % of logged wall-clock.

## PROC-903 · Split or index the lessons file to save tokens
**Retired id:** PROC-903
- **Retired:** 2026-10-07
- **Reason:** only 15 of 92 helpers read it, ~93k tokens in total (< 0.3 h); below the 3× payback rule.
- **Evidence:** arrows-game `docs/process/speed-audit-2026-10-07.md` (E7).
- **Reopen only if:** the ledger shows lessons reads above 1 h per window.

## EXPO-901 · Cancel Reanimated animations in effect cleanup to stop "synchronouslyUpdateUIProps failed for tag" warnings
**Retired id:** EXPO-901
- **Retired:** 2026-09-25
- **Reason:** built and measured: zero change; a view whose animation had finished still failed. The registry is re-applied during the next screen's first draw.
- **Evidence:** arrows-game memory `reanimated-dead-tag-mechanism.md` (PERF-DEADTAG, Reanimated 4.5.1).
- **Reopen only if:** a Reanimated release changes the props-registry lifecycle.

## EXPO-902 · Remove visual feedback to win frames or memory
**Retired id:** EXPO-902
- **Retired:** 2026-09-01
- **Reason:** removing exit trails cut ten-level growth ~10.8 → 4.5 MB, which isolated a cause; the product kept bounded feedback (two slots, 180 ms). A trail threshold of 16 made p95 worse (19.05 → 20.08 ms).
- **Evidence:** arrows-game `docs/performance/field-guide.md` ("Keep the lessons, not just the winners").
- **Reopen only if:** the owner decides the feature should go; ablation is a diagnostic, not a product decision.

## EXPO-903 · Force Hermes GC at level boundaries
**Retired id:** EXPO-903
- **Retired:** 2026-09-01
- **Reason:** memory slope worsened ~936 → 989 KB per level.
- **Evidence:** arrows-game `docs/performance/field-guide.md`.
- **Reopen only if:** a trace shows retained references are gone and only collection timing remains.

## UI-901 · Gate contrast on an element's body fill
**Retired id:** UI-901
- **Retired:** 2026-10-01
- **Reason:** meeting it darkened a light art colour to chocolate brown; legibility is carried by the outline.
- **Evidence:** arrows-game `docs/engineering-lessons.md` ("A contract rule can be wrong").
- **Replaced by:** UI-004.

## Candidates rejected by the tool-reliability study (2026-10-07)
Source for all three: `~/.claude/process-metrics/reports/tool-reliability-2026-10-07.md` ("Rejected candidates"); extract in `skills/tool-reliability/evidence/tool-study.md`. They never became rules; their ids are reserved so they are not added without new evidence.

## TOOL-901 · Always use absolute paths in shell commands
**Retired id:** TOOL-901
- **Retired:** 2026-10-07
- **Reason:** file-not-found rate is the same for absolute and relative paths within the same agent (OR 0.92 [0.50–1.69]); the raw gap in other failures is a different command mix.
- **Reopen only if:** a within-agent comparison on a specific failure class shows a difference.

## TOOL-902 · Wrap shell commands in `sh -c` to avoid zsh
**Retired id:** TOOL-902
- **Retired:** 2026-10-07
- **Reason:** no within-agent difference (OR 0.65 [0.41–1.04]; zsh-class errors only 0.47 [0.15–1.50]). Quoting fixes the zsh failures (TOOL-002).
- **Reopen only if:** a larger within-agent sample separates the arms.

## TOOL-903 · Use the Grep and Glob tools instead of grep and find
**Retired id:** TOOL-903
- **Retired:** 2026-10-07
- **Reason:** the tools were never called in 135k calls (not exposed in these sessions), so there is no evidence either way.
- **Reopen only if:** the tools are available and a within-agent comparison exists.
