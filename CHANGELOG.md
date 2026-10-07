# Changelog

## 0.2.0 · 2026-10-07

Folds in the day's measured results and syncs the tool rules with the owner's new `~/.claude/CLAUDE.md` §11 "Tool use, measured" (adversarially reviewed), which is now the authority for tool and wait rules. Sources: arrows-game `docs/process/speed-experiments-2026-10-07.md`, `agent-memory-tools-2026-10-07.md`, `graphify-trial-2026-10-07.md`, commit `ca0b0f5` (owner approves E3 and E1), and `~/.claude/process-metrics/reports/tool-reliability-2026-10-07.md`.

- **Builds.** ANDR-003 is VERIFIED: E3 fingerprint-gated incremental test builds, 598 → 88 s median, null spread 133 s, 3/3 pairs faster, 3/3 APKs byte-identical, Kotlin and TS controls pass, owner-approved; store builds stay clean (STORE-002). ANDR-002 now rests on E1's bytes (947 shared entries identical, only x86_64 removed); its time saving is INFERRED (−237 s inside a 429 s null spread).
- **New skill `code-and-doc-lookup`.** LOOK-001 narrow retrieval (heuristic, INFERRED: hindsight control); LOOK-002 library facts from the installed version (fact, VERIFIED: Context7 2 of 10 wrong-version); PROC-003 moved here and extended with a known-answer query before trusting an empty or short index answer (Serena 2 of 12 silent sessions).
- **`tool-reliability` synced with §11.** TOOL-001 cites only the Read/Edit/Write odds and §11's caveats (classifier and guard confound; turns, not hours); TOOL-002 adds the `bfs` `find` trap; TOOL-005 and TOOL-006 become invariants (TOOL-006 adds the coordinator's end-of-turn check); new TOOL-007 worktree-guard fact, TOOL-008 "state what changed" (expires 2026-11-06, 30 days of hook data), TOOL-009 a cap hit is blocked time, not a dead command.
- **`agent-process`.** PROC-001 states the 2-min default, the "foreground `timeout` above 120000 is a defect" gate, and §11's numbers (218 of 257 cap hits at a self-raised timeout, a 13 h loop); the Monitor/background odds ratios are now labelled definitional. The `fg-wait-guard` hook is described as an experiment pending owner registration, with its success criteria; it is not a rule.
- **`testing-gates`.** TEST-003's gate requires the planned n (early stopping flipped 15 of 87 verdicts).
- **Retired** (`retired/`): TOOL-003 (one simple command per call, general form), TOOL-004 (hard stop after 2 failures), TOOL-904 (dispatch hygiene, n=3), TOOL-905 (skill-table recommendations), TEST-902 (E2 early-stop rule E2-R1), LOOK-901 Serena, LOOK-902 ast-grep as default, LOOK-903 Context7; each with numbers, traps and reopen conditions. PROC-901 Graphify re-checked: still retired.
- **Evals.** ev11-long-command-timeout (§11 wait invariant: no foreground `timeout` above 120000, one run, output read); ev12-installed-library-facts (LOOK-002). Neither has been run.
- **Not made rules:** E4's load gate (n=15, project tooling; recorded as TOOL-005 evidence); §11's browser-pane, permission-layer and script-on-one-input items (body budget; numbers kept in `tool-reliability/evidence/tool-study.md`, browser deferred to `anthropic-skills:built-in-browser`).
- Totals: 10 skills, 59 rules (55 VERIFIED, 4 INFERRED; 34 invariants, 16 facts, 9 heuristics); descriptions ~368 tokens by chars/4, ~658 always-on by `claude plugin details`.

### Rulings
- **R12 · New skill instead of growing two full ones.** `agent-process` reached ~1,538 tokens with the hook note and `tool-reliability` ~1,489 with the §11 sync, so the lookup rules and PROC-003 moved to `code-and-doc-lookup`. PROC-003 keeps its id; ids are not tied to skills.
- **R13 · Retire, not rewrite, when the advice reverses.** TOOL-003 and TOOL-004 changed meaning under §11, so their ids were retired and the replacements got new ids (TOOL-007, TOOL-008); an old report citing TOOL-003 still means what it said. TOOL-005 and TOOL-006 kept their ids because their meaning only tightened.
- **R14 · E1 lives in ANDR-002.** One rule with a split confidence line ("VERIFIED — bytes; the time saving is INFERRED") rather than a second ABI rule. The lint counts it as VERIFIED.
- **R15 · Invariants by owner policy count as VERIFIED** when the harm they prevent is measured (TOOL-006: 134 parked agents), as PROC-007 already does; the hand-back's effect itself is untested and the Confidence line says so.
- **R16 · §11's numbers are quoted as §11's.** Several (245/257, 206/257, ≥ 3× the work) are not in the study text; the evidence extract names §11 as their source. The `find` exit-0 claim was re-run: silent only inside a pipeline.
- **R17 · PROC-001 keeps both §11 wait invariants in one rule** (no block past 2 min; every wait ends on failure and a deadline) to stay inside the body budget.
- **R18 · Always-on projection above 600.** Claude Code projects ~658 tokens (chars/4: ~368, under the lint's 600). Left as is: the lint budget is chars/4 by R3; trimming every description again is the owner's call.

## 0.1.1 · 2026-10-07 (local, unpublished)

Filled the pending tool-reliability section from `~/.claude/process-metrics/reports/tool-reliability-2026-10-07.md` and `.json` (135k calls, 34 projects, 2.9 % failed).

- New skill `tool-reliability`: TOOL-001 file tools (heuristic, VERIFIED), TOOL-002 zsh quoting (fact, VERIFIED), TOOL-003 simple commands (heuristic, VERIFIED), TOOL-004 loop breaker (heuristic, INFERRED: threshold untested), TOOL-005 host load is a condition (fact, VERIFIED, association), TOOL-006 blocked subagents hand back (heuristic, INFERRED: effect untested).
- PROC-001 now covers commands expected to run over ~2 min and cites the study (39.0 h + 22.4 h lost; odds 0.06 and 0.03).
- `retired/`: TOOL-901 absolute paths, TOOL-902 `sh -c` wrapping, TOOL-903 Grep/Glob tools, which the study rejected.
- Not turned into rules: the browser-tool items (association only), Read-before-Edit (the harness already enforces it), dispatch hygiene (3 cases, INFERRED, small), and the proposed wait-blocking hook (owner configuration, not a playbook rule).
- Totals: 9 skills, 56 rules (51 VERIFIED, 5 INFERRED; 32 invariants, 14 facts, 10 heuristics); descriptions ~324 tokens by chars/4, ~594 always-on by `claude plugin details`.

### Rulings
- **R10 · New skill instead of growing `agent-process`.** Six more rules would push `agent-process` past the 1,500-token body budget (it is at 1,464). They share one trigger (shell and tool use), so they became `tool-reliability`; `agent-process` keeps a pointer where the Pending section was.
- **R11 · Count discrepancy.** The study's hand-written summary says 135,022 calls and 3,974 failures; its regenerated data section says 135,035 and 3,976. The evidence extract quotes the data section and notes both.

## 0.1.0 · 2026-10-07 (local, unpublished)

First version: 8 skills, 50 rules (47 VERIFIED, 3 INFERRED; 32 invariants, 12 facts, 6 heuristics), 24 evidence files, 8 retired ideas, lint and applicability tools with self-tests, and a designed but unrun eval harness (10 cases).

Sources: the global harness (`~/.claude/CLAUDE.md` §1–§10), arrows-game `docs/engineering-lessons.md`, `docs/process/speed-audit-2026-10-07.md`, `docs/process/graphify-trial-2026-10-07.md`, `docs/performance/field-guide.md`, `docs/skins/README.md`, `docs/next-level/reports/*`, and project memory of arrows-game, geoguesser-app and sibling projects (block-blaster, lucky-shelf, merge-kit, planet-drop, secret-dictator(-v2), tondo, form-studio, morse-code-trainer, snaxx-tech, wordle, apollonia-events, gold-pdf-bot, manga-reader, futurisma-race, offbeat). Quotes from sibling memory were spot-checked against the files before use.

### Rulings (judgement calls made without the owner; reverse any of them by editing this list)

- **R1 · `neon-postgres` became `data-persistence`.** Our Neon evidence is real but small (wake time, timeouts, pooler, outages), and the strongest replicated data lesson is the save-wipe scar from client persistence. One skill covers both. The new name also avoids colliding with the owner's existing `neon-postgres` skill, which it defers to.
- **R2 · Kinds and staleness.** Invariants are exempt from the 90-day staleness warning (they never expire) but still need a valid `last_validated`. Facts and heuristics warn after 90 days; an expired heuristic warns in the lint and is labelled EXPIRED by `check-applicability.py` rather than failing the build, so the repo does not break on a calendar date.
- **R3 · Token estimate.** Budgets use chars/4, as specified. `claude plugin details` projects ~546 always-on tokens (under 600) and 1.7k–2.3k per body on invoke, about 1.5× the chars/4 figure. Meeting 1,500 on Claude Code's projection would mean ~4 rules per skill; left for the owner to decide.
- **R4 · Gate checklist.** Each SKILL.md keeps a one-line gates checklist that points at rule ids instead of repeating the gate text, to stay inside the body budget.
- **R5 · Applicability statuses.** Exactly the three asked for. A rule whose `ctx:` context is absent from the project is UNKNOWN with the reason "ctx not detected"; a rule with no version or context tokens is version-free and APPLIES.
- **R6 · Manifest owner.** `marketplace.json` names "agent-playbooks maintainers" and `plugin.json` has no author: no personal data until the owner confirms the name. `claude plugin validate` passes with one warning (no author); `--strict` fails on that warning only.
- **R7 · Eval harness on `claude plugin eval`.** The installed CLI ships an eval runner with case files, graders and a with/without-plugin ablation arm, so the cases use its `case.yaml` format instead of a custom runner. `evals/run-evals.py` prints the commands and holds the decision rule; it never starts a model session.
- **R8 · Skill-writing TDD.** `superpowers:writing-skills` asks for pressure tests with subagents before each skill. That role is assigned to the eval harness (with/without arms, replicated), which the owner asked to be designed but not run; no baseline was run in v0.1.
- **R9 · Pending section stays a stub.** `~/.claude/process-metrics/reports/` does not exist yet and no tool-reliability study was found anywhere, so the `agent-process` section names where its data will come from and holds no rules.
