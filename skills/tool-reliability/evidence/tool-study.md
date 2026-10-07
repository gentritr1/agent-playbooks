# Cross-project tool-reliability study (2026-10-07)

**Source:** `~/.claude/process-metrics/reports/tool-reliability-2026-10-07.md` and `.json` (harness-audit 1.3, generated 2026-10-07 03:32). Window 2026-06-24..2026-10-07, 34 project keys, 1,474 transcripts after removing forked-session copies.

**Also:** `~/.claude/CLAUDE.md` §11 "Tool use, measured" (owner rule, adversarially reviewed 2026-10-07). §11 is the authority for kinds and numbers. 218 of 257 (cap hits at a self-raised timeout) is §11's; the claim that a chained call does several units of work is [inferred] and unmeasured.

Tags as in the study: **measured** = computed from transcripts; **inferred** = reasoning on the data, untested; **association** = correlation only. Hours lost = failed call time + the agent's reaction gap (capped at 10 min): an estimate, not a counterfactual.

**Counts.** 135,035 paired calls; 3,976 failures (2.9 %). 93.8 % of failures have a named cause.

## Within-agent failure odds (Mantel-Haenszel, strata = agents that used both arms) [measured]
| A vs B | OR [95 % CI] | raw A vs B |
|---|---|---|
| Read vs cat/head/tail/sed -n | 0.23 [0.16–0.33] | 0.5 % vs 1.7 % |
| Edit vs sed -i/perl/script rewrite | 0.43 [0.31–0.59] | 1.5 % vs 2.6 % (sed -i also exits 0 on no match) |
| Write vs heredoc/tee | 0.09 [0.05–0.16] | 0.7 % vs 4.6 % |
| ranged Read vs whole-file Read | 0.35 [0.16–0.77] | 0.3 % vs 0.6 % (definitional: a ranged Read cannot hit the size limit) |
| long command background vs foreground | 0.03 [0.01–0.09] | 0.3 % vs 6.8 % (definitional: a detached launch cannot hit the cap) |
| Monitor vs until/while+sleep | 0.06 [0.02–0.18] | 1.6 % vs 23.3 % (definitional: Monitor does not block the turn) |
| compound (multi-line or 3+ chained) vs simple Bash | 2.07 [1.88–2.28] | 3.8 % vs 2.0 % |
| sh -c / bash script vs plain zsh | 0.65 [0.41–1.04] | no within-agent difference |
| absolute vs relative paths, file-not-found | 0.92 [0.50–1.69] | no difference |

The Grep and Glob tools were never called (0 of 135k), so no comparison exists for them.

The three rows marked definitional are not evidence for a rule: the detached arm cannot fail the way the blocking arm does. Rules cite the hours and cap hits instead. §11 adds that part of the Read/Edit/Write gap is the classifier and worktree guard that Bash hits and the file tools do not, and that the saving is turns, not hours.

## zsh-specific failures [measured]
437 in total: `=`-leading word expansion 284, unquoted glob no-match 129, `$VAR` not word-split 15, other 9 (about 1.4 h, mostly geoguesser-app and arrows-game). 248 of 298 worktree-guard rejections were compound commands.

## Hours lost and loops [measured]
| Pattern | n | Hours |
|---|---|---|
| foreground wait loop hit its limit | 257 | 39.0 |
| long non-wait command timed out (202 were moved to the background and kept running; of 269 non-wait timeouts, 8 were later followed by a passing identical rerun, rerun count not measured) | 261 | 22.4 |
| waits that ended in a timeout (incl. background waits that never matched; one ran 13 h) | 284 | 64.7 |
| identical failing call retried 3+ times (21 ended in success, 20 abandoned) | 41 | 3.7 tool / 10.0 span |
| 3+ consecutive failures of one tool | 46 | 9.2 |
| subagents parked on the coordinator (median 15 min, p90 107 min; one parked ~9.7 days) | 134 | 105.8 capped at 8 h/agent (334.8 raw), elapsed time not compute |

Foreground waits hitting the 10-min cap: 196 of 69,774 Bash calls before the §9 rule (0.28 %), 35 of 8,885 after it (0.39 %): no detectable improvement in pooled data (association); arrows-game 0.94 % → 0.48 %, geoguesser flat (0.30 % → 0.39 %, within count noise), 2-day window. Re-computed 2026-10-07 from harness-audit 1.5 digests.

## Concurrency [measured; association]
Failure rate 2.9 / 2.5 / 2.9 / 2.6 % at 1 / 2 / 3 / 4+ concurrently active projects. Median Bash file-read latency 0.08 s → 1.06 s and Read 0.02 → 0.06 s from 1 to 4+ projects. 8 timeouts were re-labelled host-load-passed-on-rerun.

## §11 numbers used by the rules
- **Cap hits (PROC-001, TOOL-009):** 218 of 257 foreground-wait cap hits ran to the 10-min cap (≥ 590 s on a 120 s default, because the agent raised its own `timeout`); 202 of 261 long-command timeouts were moved to the background and kept running. Of 269 non-wait timeouts, 8 were later followed by a passing identical rerun; the number of reruns itself is not measured.
- **Retries (TOOL-008):** 41 identical-retry loops, 3.7–10 h; 21 eventually succeeded, so a hard stop after 2 failures would also cut successes. §11 replaced the study's stop rule with "state what changed". Re-measure with a harness-audit run on 2026-11-06, not from hook data: the hook logs decisions, not outcomes.
- **Compound commands (TOOL-007):** 3.8 % vs 2.0 % per call (OR 2.07) [measured]; a chained call does several units of work, so splitting is unlikely to lower total failures [inferred; work per call not measured]. The guard's 298 rejections in worktree agents are the real cost: 248 compound, 132 mutating, 71 `cd` (futurisma-race 199).
- **Subagents (TOOL-006):** 134 parked (median 15 min, p90 107 min, one 9.7 days). §11 makes the hand-back and the coordinator's end-of-turn check invariants.
- **Conditions (TOOL-005):** failure rate flat at 2.5–2.9 %, fs-read latency up 13×; §11 asks for loadavg at brief time because transcripts do not carry it.
- **Kept out of rules (budget; small):** the permission layer costs turns, not fixes (classifier unavailable 93, denied 71, about 3 h): back off once and continue with other work. Run your own analysis script on one input before the full set (86 Python + 84 Node tracebacks, 1.8 h; INFERRED). Browser pane: front a hidden or stuck pane or ask, since a repeat fails identically (233 pane timeouts; n = 3 identical retry loops, all still failing); wrap `javascript_tool` code in an async IIFE (41 errors).

## `find` is `bfs` (re-run 2026-10-07)
§11: `find` in the agent shell is a function wrapping `bfs`, which fails silently (exit 0) on directories whose names begin with `-`. Re-run in a scratch directory: `find -dashdir -name '*.txt'` printed `bfs: error: Unknown argument` and exited 1 on its own, but `find -dashdir … 2>/dev/null | wc -l` printed 0 with exit 0, which is the silent case. `find ./-dashdir …` found the file.

## Dropped by §11 (see `retired/`)
- "One simple command per call" in its general form (old TOOL-003); only the worktree fact remains (TOOL-007).
- A hard stop after 2 identical failures (old TOOL-004); replaced by TOOL-008.
- Dispatch hygiene: 3 re-dispatches, all one project on one day (TOOL-904).
- The skill-usefulness table's recommendations: associations, outcome known for 1 invocation (TOOL-905).

## arrows-game load gate (E4, 2026-10-07)
**Source:** arrows-game `docs/process/speed-experiments-2026-10-07.md` (E4). `scripts/process/load-gate.sh` records 1/5/15-min load, CPU count and foreign Gradle/jest/emulator processes, and can wait until the 1-min load is below 1.0 × CPUs. Threshold derivation is weak: 15 jest runs with a nearby load sample; below 1.0 per CPU 5 of 5 took 50–80 s, at or above it 5 of 10 took 89–263 s. The host sat at load 12–61 all day, so every 8.0 wait would have timed out. Adopted there as tooling; here it only supports TOOL-005's "record the condition", not a threshold rule.
