---
name: tool-reliability
description: Before shell file edits, zsh quoting or find, worktree commands, repeated failed calls, timeouts, parked subagents, host-load claims.
---

# Tool reliability

Synced with `~/.claude/CLAUDE.md` §11 (135k calls, 34 projects); kinds and numbers are §11's. Waits: PROC-001.

### TOOL-001 · File work goes through Read, Edit and Write
- **Rule:** Read, edit and create files with the Read, Edit and Write tools; keep the shell for pipelines, aggregates and scripts.
- **Kind:** heuristic — goal: fewer failed turns and no silent no-match edits; override: stronger case evidence, stated in the report; expires: 2027-01-05
- **Evidence:** within-agent failure odds Read 0.23, Edit 0.43, Write 0.09 vs shell forms; part of the gap is the classifier and guard Bash hits; the saving is turns, not hours → [study](evidence/tool-study.md)
- **Confidence:** VERIFIED — within-agent odds ratios whose CIs exclude 1
- **Gate:** no `sed -i`, heredoc or `cat >` file writes
- **Valid while:** this permission mode and sandbox (re-measure when either changes) · last_validated: 2026-10-07
- **Source:** TOOL-001

### TOOL-002 · zsh and `find` need care where bash does not
- **Rule:** Quote words that start with `=` and globs passed as arguments, never run an unquoted `$VAR` of arguments, and write `./-dir` for a directory whose name starts with `-`.
- **Kind:** fact — zsh expands `=word`, aborts on an unmatched glob and does not word-split; `find` is a `bfs` wrapper that reads `-dir` as an option, silently (exit 0) in a pipeline.
- **Evidence:** zsh failures `=` 284, glob 129, `$VAR` 15; `sh -c` is not the fix (OR 0.65 [0.41–1.04]); `bfs` re-run 2026-10-07 → [study](evidence/tool-study.md)
- **Confidence:** VERIFIED
- **Gate:** no `= not found`, `no matches found` or `bfs: error` in the session
- **Valid while:** macOS default zsh, `find` wrapped by `bfs` · last_validated: 2026-10-07
- **Source:** TOOL-002

### TOOL-007 · Worktree agents use simple commands; others may chain
- **Rule:** In a worktree agent, send no compound, `cd` or chained mutating command; elsewhere keep compound commands.
- **Kind:** fact — the worktree guard rejects those forms. Compound calls fail 3.8 % vs 2.0 % (OR 2.07, measured); [inferred] each does several units of work, so splitting is unlikely to lower total failures.
- **Evidence:** 298 guard rejections (248 compound, 132 mutating, 71 `cd`) → [study](evidence/tool-study.md)
- **Confidence:** VERIFIED — rejections, per-call odds; splitting claim INFERRED
- **Gate:** no worktree-guard rejection in a worktree agent's transcript
- **Valid while:** Claude Code worktree guard · `claude-code@2.1` · last_validated: 2026-10-07
- **Source:** TOOL-007

### TOOL-008 · A repeated identical call says what changed
- **Rule:** Before repeating an identical call, state what changed since it failed (time, input, environment); if nothing did, change the input.
- **Kind:** heuristic — goal: no blind retry loops without cutting retries that succeed; override: stronger case evidence, stated in the report; expires: 2026-11-06
- **Evidence:** 41 identical-retry loops cost 3.7–10 h; 21 ended in success, so a hard stop would cut successes too → [study](evidence/tool-study.md)
- **Confidence:** INFERRED — the effect is untested; re-measure with a harness-audit run on 2026-11-06 (the hook logs no outcomes)
- **Gate:** a repeated identical failed call names a change in its description
- **Valid while:** any tool · last_validated: 2026-10-07
- **Source:** TOOL-008

### TOOL-009 · A cap hit is blocked time, not a dead command
- **Rule:** After a timeout, read the moved command's background output; never rerun it.
- **Kind:** fact — the harness moves a capped command to the background, where it keeps running.
- **Evidence:** 218 of 257 foreground-wait cap hits ran to the 10-min cap; 202 of 261 long-command timeouts were moved to the background and kept running; of 269 non-wait timeouts, 8 were later followed by a passing identical rerun (rerun count not measured) → [study](evidence/tool-study.md)
- **Confidence:** VERIFIED
- **Gate:** after a timeout the next call reads that task's output; no rerun while it runs
- **Valid while:** Claude Code Bash tool, 2-min default · `claude-code@2.1` · last_validated: 2026-10-07
- **Source:** TOOL-009

### TOOL-005 · A condition is not a cause until an identical rerun passes
- **Rule:** Record loadavg at brief time, and blame load or any other condition only when the identical rerun passes.
- **Kind:** invariant — why: load was blamed for failures it did not cause; transcripts lack loadavg.
- **Evidence:** failure rate flat at 2.5–2.9 % with 1 to 4+ concurrent projects while fs-read latency rose 13× → [study](evidence/tool-study.md)
- **Confidence:** VERIFIED — association across 135k calls
- **Gate:** a condition named as a cause cites the passing identical rerun; loadavg is recorded
- **Valid while:** shared host, several sessions · last_validated: 2026-10-07
- **Source:** TOOL-005

### TOOL-006 · Blocked subagents hand back; coordinators leave none parked
- **Rule:** A blocked subagent hands back a partial report and stops; a coordinator answers or stops every live subagent before ending its turn.
- **Kind:** invariant — why: parked agents hold wall-clock and work for hours or days, unread.
- **Evidence:** 134 agents parked, median 15 min, p90 107 min, one 9.7 days → [study](evidence/tool-study.md)
- **Confidence:** VERIFIED — parking measured; hand-back effect untested (§11 policy)
- **Gate:** every brief carries the hand-back line; no live subagent is unanswered at turn end
- **Valid while:** subagent dispatch · last_validated: 2026-10-07
- **Source:** TOOL-006

## Gates before you report done
File tools (001); no zsh or `bfs` errors (002); no guard rejection (007); repeats name a change (008); timeouts read, not rerun (009); conditions cite a rerun (005); no parked agent (006).

## Not covered / defer to
Waits: PROC-001. Browser pane, permission denials, script-on-one-input: §11 notes in [study](evidence/tool-study.md); browser: `anthropic-skills:built-in-browser`. Debugging: `superpowers:systematic-debugging`.
