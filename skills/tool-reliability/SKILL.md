---
name: tool-reliability
description: Use before shell file edits, chained or quoted zsh commands, retrying a failed call, leaving a subagent waiting, or blaming host load.
---

# Tool reliability

From the 2026-10-07 study of 135k tool calls across 34 projects (2.9 % failed). Waits and long commands are in PROC-001. The study's own rule list is a draft under owner review; rules taken from its inferred parts are INFERRED here.

### TOOL-001 · File work goes through Read, Edit and Write
- **Rule:** Read, edit and create files with the Read, Edit and Write tools, using offset/limit for large files; keep the shell for pipelines and counts.
- **Kind:** heuristic — goal: fewer failed calls and no silent no-match edits; override: stronger case evidence, stated in the report; expires: 2027-01-05
- **Evidence:** within-agent failure odds: Read vs cat/sed 0.23, Edit vs `sed -i` 0.43, Write vs heredoc 0.09, ranged Read 0.35 → [study](evidence/tool-study.md)
- **Confidence:** VERIFIED — within-agent odds ratios whose CIs exclude 1
- **Gate:** no `sed -i`, heredoc or `cat >` file writes in the session's tool calls
- **Valid while:** Claude Code file tools, macOS · last_validated: 2026-10-07
- **Source:** TOOL-001

### TOOL-002 · zsh needs quoting where bash does not
- **Rule:** Quote words that start with `=` and globs passed as arguments, and never run a command stored in an unquoted `$VAR`.
- **Kind:** fact — zsh expands `=word`, aborts on an unmatched glob, and does not word-split variables.
- **Evidence:** 437 zsh failures: `=` expansion 284, glob no-match 129, unsplit `$VAR` 15; `sh -c` wrapping showed no within-agent difference → [study](evidence/tool-study.md)
- **Confidence:** VERIFIED
- **Gate:** no `= not found` or `no matches found` shell errors in the session
- **Valid while:** macOS default zsh in the agent shell · last_validated: 2026-10-07
- **Source:** TOOL-002

### TOOL-003 · One simple command per call
- **Rule:** Prefer one simple command per Bash call over multi-line or 3+-step chains.
- **Kind:** heuristic — goal: fewer failed and guard-rejected calls; override: stronger case evidence, stated in the report; expires: 2027-01-05
- **Evidence:** compound commands failed more often within the same agent (OR 2.07); 248 of 298 worktree-guard rejections were compound → [study](evidence/tool-study.md)
- **Confidence:** VERIFIED — within-agent odds ratio
- **Gate:** a state change and its bookkeeping are separate calls (PROC-006)
- **Valid while:** Claude Code Bash tool · last_validated: 2026-10-07
- **Source:** TOOL-003

### TOOL-004 · Break a retry loop after two identical failures
- **Rule:** After the same call fails twice, read the error and change the input or approach before trying again.
- **Kind:** heuristic — goal: no repeated identical failures; override: stronger case evidence, stated in the report; expires: 2027-01-05
- **Evidence:** 41 loops of 3+ identical failing calls (3.7–10.0 h), 20 abandoned anyway; 46 failure streaks (9.2 h) → [study](evidence/tool-study.md)
- **Confidence:** INFERRED — the study did not test the threshold of 2 against a counterfactual
- **Gate:** no identical call fails 3 times in the transcript
- **Valid while:** any tool · last_validated: 2026-10-07
- **Source:** TOOL-004

### TOOL-005 · Host load is a condition, not a cause
- **Rule:** Record concurrency and load with timing work, and blame load for a failure only when the identical rerun passes.
- **Kind:** fact — concurrency raised latency but not the failure rate.
- **Evidence:** failure rate 2.5–2.9 % at 1 to 4+ active projects; file-read latency 0.08 → 1.06 s; 8 timeouts passed on rerun → [study](evidence/tool-study.md)
- **Confidence:** VERIFIED — association across 135k calls
- **Gate:** a "host load" explanation cites the passing identical rerun
- **Valid while:** shared macOS host, several sessions · last_validated: 2026-10-07
- **Source:** TOOL-005

### TOOL-006 · A blocked subagent hands back instead of waiting
- **Rule:** Every brief says what to do when blocked: hand back a partial report, and the coordinator answers parked agents before new dispatch.
- **Kind:** heuristic — goal: less elapsed time with agents idle; override: stronger case evidence, stated in the report; expires: 2027-01-05
- **Evidence:** 134 subagents parked on the coordinator, p90 107 min, 105.8 h capped (one ~9.7 days) → [study](evidence/tool-study.md)
- **Confidence:** INFERRED — the study marks the hand-back effect as untested
- **Gate:** the brief has a "when blocked" line; no agent waits over 30 min unanswered
- **Valid while:** subagent dispatch · last_validated: 2026-10-07
- **Source:** TOOL-006

## Gates before you report done
File tools (001); no zsh-class errors (002); separate state changes (003); no third identical failure (004); load claims cite a rerun (005).

## Not covered / defer to
Waits and long commands: PROC-001. Debugging a loop: `superpowers:systematic-debugging`. Browser tool reliability: `anthropic-skills:built-in-browser`.
