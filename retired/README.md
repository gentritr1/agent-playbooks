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
- **Reason:** 3 of 12 real questions fully correct; 4 of 4 stale answers after edits, exit 0, no warning; realistic cost vs grep plus read: median per question −7.5 %, total +11.5 % (the graph cost more).
- **Evidence:** arrows-game `docs/process/graphify-trial-2026-10-07.md`.
- **Replaced by:** PROC-003 for any cache that is used.
- **Reopen only if:** a ledger shows "who calls X" questions dominate re-read cost, and a new version checks freshness at query time and indexes literal values.
- **Re-compared 2026-10-07:** on the same 12 questions Serena and ast-grep did better (6 and 8 correct vs 3) and were also rejected (LOOK-901, LOOK-902); the tool-reliability study found no new reason (errors a code map could prevent total under 2 h).
- **Re-compared 2026-10-08:** refined grep still wins. On 12 memory questions no indexed route beat it: it was 12 of 12 correct at total −41.0 % (median per question +40.1 %); an Obsidian MCP server (LOOK-904), basic-memory (LOOK-905) and an in-house description and backlink index (11 of 12, total −37.2 %) cost more or equalled it and went stale or needed a guard. Graphify itself was not re-run; no new reason to reopen.

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
- **Re-compared 2026-10-08:** a 153-line description and backlink index (stdlib) lost to refined grep on 12 memory questions (11 of 12 correct with one grep fallback; total −37.2 % vs −41.0 %; median per question +11.2 % vs +40.1 %); with its fingerprint check off it served 3 of 3 edits stale. Reopen only if "what links to X" questions show up in the ledger.

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

## Dropped when the owner adopted §11 (2026-10-07)
Source for all four: `~/.claude/CLAUDE.md` §11 "Tool use, measured" (adversarially reviewed) and the study above; extract in `skills/tool-reliability/evidence/tool-study.md`.

## TOOL-003 · One simple command per Bash call (general form)
**Retired id:** TOOL-003
- **Retired:** 2026-10-07
- **Reason:** compound commands fail 3.8 % vs 2.0 % per call (OR 2.07, measured), but [inferred] each does several units of work, so splitting them is unlikely to lower total failures. The cost is real only in worktree agents, whose guard rejected 298 compound, `cd` or mutating forms.
- **Replaced by:** TOOL-007 (the worktree fact).
- **Reopen only if:** a per-unit-of-work comparison shows compound commands fail more outside worktree agents.

## TOOL-004 · Stop after 2 identical failures
**Retired id:** TOOL-004
- **Retired:** 2026-10-07
- **Reason:** 21 of the 41 identical-retry loops ended in success, so a hard stop would also cut successes; the threshold of 2 was never tested.
- **Replaced by:** TOOL-008 (state what changed before repeating).
- **Reopen only if:** the 2026-11-06 harness-audit run (transcripts; the hook logs no outcomes) shows identical retries rarely succeed.

## TOOL-904 · Dispatch hygiene: check the dispatch list before sending a brief
**Retired id:** TOOL-904
- **Retired:** 2026-10-07 (never a rule)
- **Reason:** 3 re-dispatches of finished work (1.55 h), all from one project on one day; with forked-session copies counted it had looked like 178. n=3 carries no rule.
- **Reopen only if:** the ledger shows repeat dispatch in 3+ projects or above 2 h a month.

## TOOL-905 · Recommendations from the skill-usefulness table
**Retired id:** TOOL-905
- **Retired:** 2026-10-07 (never a rule)
- **Reason:** associations only; the outcome was inferable for 1 skill invocation, and transcripts with any Skill call differ in task mix (long main sessions).
- **Reopen only if:** the eval harness (with/without arms) or ledger outcomes measure a skill's effect.

## Rejected route experiments (arrows-game, 2026-10-07)

## TEST-902 · Stop an A/B/A perf series early once the verdict looks settled (rule E2-R1)
**Retired id:** TEST-902
- **Retired:** 2026-10-07
- **Reason:** replayed on 87 archived series (1,894 runs) under a pre-registered rule (looks from 3 runs per arm, shift = median beyond the null spread with disjoint ranges, futility = within half the null with overlap, 2 consecutive looks). It would have saved 590 runs (31.2 %), but **15 of 87 series flipped verdict** (7 if stops on "inconclusive" series are not counted, which still rejects it): a futility stop at 6 vs 5 runs missed the improvement the full 24 vs 24 series found; a shift/no-shift rule disagreed with a "+16 ms budget" gate in both directions; it decided on data the report had ruled contaminated by load. With labels shuffled, the sequential rule claimed an effect more often than one fixed-n look in 48 of 87 series.
- **Evidence:** arrows-game `docs/process/speed-experiments-2026-10-07.md` (E2; pre-registration committed before outcomes were opened).
- **Replaced by:** TEST-003 at the planned n.
- **Reopen only if:** a new pre-registered rule is margin-aware, has no futility stop before the planned n, checks for contamination before any stop, and spends alpha so the shuffled false-effect rate stays at or below the fixed-n rate; then replay all 87 series with 0 flips.

## LOOK-901 · Serena (LSP over MCP) for code navigation
**Retired id:** LOOK-901
- **Retired:** 2026-10-07
- **Reason:** 6 of 12 correct, 4 partial (2 misleading); 76.5k chars vs 81.1k baseline plus ~32.5k fixed per session (net +34 %). Traps: it waits at most 30 s for indexing, then in 2 of 12 sessions returned empty or partial cross-file references for the whole session with the warning on server stderr only; it misses references through a structural interface; its line numbers are 0-based; its `claude-code` prompt marks Read and Edit "FORBIDDEN" and its recommended hook denies the third consecutive Grep/Read, pushing agents away from the read that would catch these; it pings a usage endpoint unless disabled.
- **Evidence:** arrows-game `docs/process/agent-memory-tools-2026-10-07.md` §2; extract in `skills/code-and-doc-lookup/evidence/tool-trials.md`.
- **Replaced by:** LOOK-001 and PROC-003's known-answer query.
- **Reopen only if:** the ledger shows cross-file refactors as a cost driver; then trial the official `typescript-lsp` plugin (same engine, no prompt takeover) with a known-answer reference query per session.

## LOOK-902 · ast-grep as the default code-search route
**Retired id:** LOOK-902
- **Retired:** 2026-10-07
- **Reason:** 8 of 12 correct, but 45.8k total chars (total −43.5 % vs baseline; median per question +39.2 %) vs 43.3k for plain grep asked with the same specificity (total −46.6 %; median per question +34.1 %): the saving is the narrow question, not the tool. Traps: `-l ts` silently skips `.tsx`; an identifier pattern skips property keys; 3 of ~25 patterns matched nothing and looked like "no results". Allowed ad hoc for structural rewrites.
- **Evidence:** as LOOK-901, §2.
- **Replaced by:** LOOK-001.
- **Reopen only if:** the eval harness shows it beats refined grep on fresh tasks written without hindsight.

## LOOK-903 · Context7 (or any unversioned docs service) for library facts
**Retired id:** LOOK-903
- **Retired:** 2026-10-07
- **Reason:** 6 of 10 version-exact questions right, 3 wrong, 2 for the wrong version (RN 0.86 compileSdk 37 / targetSdk 35, truth 36 / 36; no Reanimated 4.5 or Expo SDK 57 data); wrong answers looked as authoritative as right ones. 53k chars vs ~2k from the installed packages; wrong twice on Vercel's CDN-only header, which the official page answered.
- **Evidence:** as LOOK-901, §3.
- **Replaced by:** LOOK-002.
- **Reopen only if:** it lists the exact installed versions; then re-run questions D1–D11.

## Rejected route experiments (arrows-game, 2026-10-08): notes as agent memory

## LOOK-904 · An Obsidian MCP server (MCPVault) as agent memory
**Retired id:** LOOK-904
- **Retired:** 2026-10-08
- **Reason:** 9 of 12 memory questions correct, 3 partial, 0 wrong; to full answers total 65.8k chars vs 77.8k baseline (total −15.4 %; median per question −7.0 %, so a typical question cost more), against refined grep at total −41.0 % and median +40.1 %. 10,867 chars of tool schemas (18 tools) per session; each search re-reads every file (0.5-11 s under load); no backlink tool; its write, patch, move and delete tools are pointed at the memory (LOOK-003). Fresh after edits (3 of 3), MIT, no network code found.
- **Evidence:** arrows-game `docs/process/obsidian-memory-trial-2026-10-08.md` §3, §4; extract in `skills/code-and-doc-lookup/evidence/memory-trials.md`.
- **Replaced by:** LOOK-001 (note form) and LOOK-003.
- **Reopen only if:** the harness defers MCP schemas, a read-only mode removes the write tools, and refined grep loses on a fresh question set written without hindsight.

## LOOK-905 · basic-memory as agent memory
**Retired id:** LOOK-905
- **Retired:** 2026-10-08
- **Reason:** 10 of 12 correct, 2 partial, 0 wrong; total +1.2 % vs baseline (median per question −30.9 %); 36,730 chars of tool schemas and instructions per session; first index 979 s (16.3 min) and a CLI reindex re-embedded all 538 notes after 3 edits. Its default first sync rewrote 528 of 536 notes (LOOK-003). In the configuration that leaves notes untouched its graph returned 0 relations and `read_note("SKILL")` failed on a duplicate title. `read_note` served the old text 0.5 s after an edit (PROC-003). AGPL-3.0; 808 MB installed.
- **Evidence:** as LOOK-904.
- **Replaced by:** LOOK-001 (note form), LOOK-003 and PROC-003.
- **Reopen only if:** a release indexes without writing to the notes and resolves them by path, and then wins on a fresh question set written without hindsight.
