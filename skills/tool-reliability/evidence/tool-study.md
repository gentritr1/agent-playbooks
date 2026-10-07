# Cross-project tool-reliability study (2026-10-07)

**Source:** `~/.claude/process-metrics/reports/tool-reliability-2026-10-07.md` and `.json` (harness-audit 1.3, generated 2026-10-07 03:32). Window 2026-06-24..2026-10-07, 34 project keys, 1,474 transcripts after removing forked-session copies.

Tags as in the study: **measured** = computed from transcripts; **inferred** = reasoning on the data, untested; **association** = correlation only. Hours lost = failed call time + the agent's reaction gap (capped at 10 min): an estimate, not a counterfactual.

**Counts.** 135,035 paired calls and 3,976 failures (2.9 %) in the regenerated data section; the hand-written summary says 135,022 and 3,974. 93.8 % of failures have a named cause.

## Within-agent failure odds (Mantel-Haenszel, strata = agents that used both arms) [measured]
| A vs B | OR [95 % CI] | raw A vs B |
|---|---|---|
| Read vs cat/head/tail/sed -n | 0.23 [0.16–0.33] | 0.5 % vs 1.7 % |
| Edit vs sed -i/perl/script rewrite | 0.43 [0.31–0.59] | 1.5 % vs 2.6 % (sed -i also exits 0 on no match) |
| Write vs heredoc/tee | 0.09 [0.05–0.16] | 0.7 % vs 4.6 % |
| ranged Read vs whole-file Read | 0.35 [0.16–0.77] | 0.3 % vs 0.6 % |
| long command background vs foreground | 0.03 [0.01–0.09] | 0.3 % vs 6.8 % (launch only) |
| Monitor vs until/while+sleep | 0.06 [0.02–0.18] | 1.6 % vs 23.3 % |
| compound (multi-line or 3+ chained) vs simple Bash | 2.07 [1.88–2.28] | 3.8 % vs 2.0 % |
| sh -c / bash script vs plain zsh | 0.65 [0.41–1.04] | no within-agent difference |
| absolute vs relative paths, file-not-found | 0.92 [0.50–1.69] | no difference |

The Grep and Glob tools were never called (0 of 135k), so no comparison exists for them.

## zsh-specific failures [measured]
437 in total: `=`-leading word expansion 284, unquoted glob no-match 129, `$VAR` not word-split 15, other 9 (about 1.4 h, mostly geoguesser-app and arrows-game). 248 of 298 worktree-guard rejections were compound commands.

## Hours lost and loops [measured]
| Pattern | n | Hours |
|---|---|---|
| foreground wait loop hit its limit | 257 | 39.0 |
| long non-wait command timed out (202 hit the limit; 8 passed on rerun) | 261 | 22.4 |
| waits that ended in a timeout (incl. background waits that never matched; one ran 13 h) | 284 | 64.7 |
| identical failing call retried 3+ times (21 ended in success, 20 abandoned) | 41 | 3.7 tool / 10.0 span |
| 3+ consecutive failures of one tool | 46 | 9.2 |
| subagents parked on the coordinator (median 15 min, p90 107 min; one parked ~9.7 days) | 134 | 105.8 capped at 8 h/agent (334.8 raw), elapsed time not compute |

Foreground waits hitting the 10-min cap: 196 of 69,774 Bash calls before the §9 rule (0.28 %), 35 of 8,885 after it (0.39 %).

## Concurrency [measured; association]
Failure rate 2.9 / 2.5 / 2.9 / 2.6 % at 1 / 2 / 3 / 4+ concurrently active projects. Median Bash file-read latency 0.08 s → 1.06 s and Read 0.02 → 0.06 s from 1 to 4+ projects. 8 timeouts were re-labelled host-load-passed-on-rerun.

## Draft status
The study's "Proposed §11 rules" are drafts the owner has not ruled on. Its loop-breaker threshold (2 identical failures), dispatch hygiene and the parked-subagent hand-back are marked INFERRED there. Rejected by the study for lack of evidence: always use absolute paths, wrap scripts in `sh -c`, use the Grep tool, and rules about unchanged-tree builds or repeated test runs (under 0.3 h).
