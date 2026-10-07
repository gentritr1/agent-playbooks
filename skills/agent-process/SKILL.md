---
name: agent-process
description: Use before delegating to a subagent or Codex, waiting on a long command, using worktrees, merging, committing or deleting, trusting a cache or index, or changing how the work itself is done to make it faster.
---

# Agent process

How the work is run, measured across ~93 helper runs and several projects. The owner's global harness sets the policy; these rules carry its measured scars.

### PROC-001 · Never block on a wait
- **Rule:** Run waits in the background, exit on success or failure, and wait on a PID or sentinel file.
- **Kind:** invariant — why: foreground loops burn the tool cap and orphaned loops load the host for days.
- **Evidence:** 2026-10-05: 219 calls hit the 10-min cap (37 h); arrows-game 2026-09-29: seven `pgrep -f` loops matched themselves and ran ~42 h → [waits](evidence/waits.md)
- **Confidence:** VERIFIED
- **Gate:** no foreground poll over 30 s; every wait condition also matches failure (`kill -0 $PID`, a FAILED marker)
- **Valid while:** Claude Code Bash tool, 10-min cap · last_validated: 2026-10-07
- **Source:** PROC-001

### PROC-002 · Speed decisions come from the ledger
- **Rule:** Answer "why is it slow" from measured task data, and test a new route against the old one, interleaved, before adopting it.
- **Kind:** invariant — why: intuition named the wrong bottleneck, and verification may get cheaper but never thinner.
- **Evidence:** arrows-game 2026-10-07: builds were guessed to dominate but were 6.2 % of 101.3 h; model time 34 %, perf series 23 % → [speed-audit](evidence/speed-audit.md)
- **Confidence:** VERIFIED
- **Gate:** one ledger line per brief; a route change shows ≥3 interleaved reps per arm, the null spread and an unchanged quality gate
- **Valid while:** owner harness §10 · last_validated: 2026-10-07
- **Source:** PROC-002

### PROC-003 · A cache or index is checked against the tree before use
- **Rule:** Stamp any index, graph or summary with the commit and a hash of uncommitted changes, and refuse it on mismatch.
- **Kind:** invariant — why: a code graph answered from an edited tree with old answers, exit 0, no warning.
- **Evidence:** arrows-game 2026-10-07: Graphify returned 4 of 4 stale answers labelled `EXTRACTED`; 3 of 12 answers fully correct; a stamp guard cost 0.3 s → [graphify](evidence/graphify.md)
- **Confidence:** VERIFIED
- **Gate:** an invalidation test: edit a file and the guard refuses the old answer
- **Valid while:** any derived index · last_validated: 2026-10-07
- **Source:** PROC-003

### PROC-004 · Briefs stand alone; reviews re-run the failure
- **Rule:** Give delegates a self-contained brief with non-goals, observable acceptance and the review command, and review by re-running the original failure.
- **Kind:** invariant — why: delegates lack this conversation, and reading a diff misses what a re-run catches.
- **Evidence:** arrows-game 2026-10-04: Codex stopped 6 times on real plan conflicts in each of two plans; secret-dictator: independent re-runs caught something the report missed in every one of 4 rounds → [delegation](evidence/delegation.md)
- **Confidence:** VERIFIED
- **Gate:** the brief has context, non-goals, acceptance and verification; the review records the re-run command and its before/after
- **Valid while:** subagents and Codex CLI · last_validated: 2026-10-04
- **Source:** PROC-004

### PROC-005 · One implementer per worktree, cut from a stated SHA
- **Rule:** Create each worktree yourself from a stated HEAD, give it one implementer, and copy its ignored evidence out before removing it.
- **Kind:** invariant — why: shared checkouts and wrong bases corrupted work in five projects.
- **Evidence:** geoguesser 2026-10-02: an isolated worktree was cut from `main`, not the feature branch (same in 2 more projects); 2026-10-04: `worktree remove --force` deleted all ignored evidence → [delegation](evidence/delegation.md)
- **Confidence:** VERIFIED
- **Gate:** the delegate prints `git rev-parse HEAD` equal to the stated SHA; test runs count only this tree's suites
- **Valid while:** `ctx:git` · last_validated: 2026-10-06
- **Source:** PROC-005

### PROC-006 · State changes stand alone; bookkeeping follows a read result
- **Rule:** Run each merge, commit or push as its own step and read its result before any ledger, cleanup or next cut.
- **Kind:** invariant — why: a failed merge chained with `;` was logged as merged and its worktree deleted.
- **Evidence:** geoguesser 2026-10-04: the suite showed 2219 tests, not 2275, the unread tell; 2026-10-02: a 904/905 run was committed → [delegation](evidence/delegation.md)
- **Confidence:** VERIFIED
- **Gate:** the merged suite's test count equals the branch's before any ledger line
- **Valid while:** `ctx:git` · last_validated: 2026-10-04
- **Source:** PROC-006

### PROC-007 · Outward and irreversible steps need the owner's yes each time
- **Rule:** Ask before every push, merge to main, publish, store submission or deletion, and delete only outside a keep-list built from the reports.
- **Kind:** invariant — why: approvals do not carry over, and an emergency cleanup deleted eight owner-acceptance videos.
- **Evidence:** arrows-game 2026-09-27: `find … -delete` removed 8 `owner-*.mp4` files; 2026-10-01: each push needed its own yes → [delegation](evidence/delegation.md)
- **Confidence:** VERIFIED
- **Gate:** the report quotes the owner's yes per outward step; deletions print the keep-list first
- **Valid while:** owner-run projects · last_validated: 2026-10-01
- **Source:** PROC-007

## Pending: cross-project tool-reliability study 2026-10-07
Not yet available: `~/.claude/process-metrics/reports/` does not exist and only `arrows-game.jsonl` is in the ledger. Fill this section from those reports when they land, as rules with the standard fields.

## Not covered / defer to
Parallel dispatch: `superpowers:dispatching-parallel-agents`, `superpowers:subagent-driven-development`. Worktree mechanics: `superpowers:using-git-worktrees`.
