# Waits

**Source:** `~/.claude/CLAUDE.md` §9 (measured 2026-10-05 over 123k tool calls, 2026-06-24..10-05); arrows-game `docs/process/speed-audit-2026-10-07.md` (E13, "The 15 slowest single calls"); arrows-game memory `shared-host-contention.md` (2026-09-29 orphaned loops), `re-ceiling-gotchas.md`, `w5-art-batch-gotchas.md`, `polish-t11-gate-gotchas.md`.

- Global: 219 Bash calls ran into the 10-min cap (37 h), every one in the foreground; the same loops run in the background cost ~0. Fresh-browser screenshot harnesses ran 30 s–2.6 min each; 24 of 50 harnesses launched a fresh browser, 21 used fixed sleeps, 0 reused one.
- arrows-game helpers: 605 foreground wait loops, 142 hit the cap and were re-issued; all 15 slowest calls were capped foreground waits (601–644 s). Re-issuing costs a turn at ~280k context (E13 estimate ~0.4 h model time).
- 2026-09-29: seven background loops (`until ! pgrep -f "loopps.mjs"` and similar) ran ~42 h after their targets finished, because `pgrep -f NAME` matches the loop's own shell command line. The controller could not kill them; the owner had to.
- POLISH-T11: a `nohup`/`&` waiter survived although `ps | grep` missed it, so two chains drove the device at once; use background runs only and check the PID tree for duplicates.
- Recommended form (E13): `until [ -f DONE ] || [ -f FAILED ] || ! kill -0 $PID; do sleep 5; done`, run in the background.

## Cross-project study (2026-10-07)
**Source:** `~/.claude/process-metrics/reports/tool-reliability-2026-10-07.md` (135k calls, 34 projects, 2026-06-24..10-07); full extract in [tool-study](../../tool-reliability/evidence/tool-study.md).
- Foreground wait loops that hit their limit: 257, 39.0 h; long non-wait foreground commands that timed out: 261, 22.4 h (202 hit the limit, 8 passed on rerun); waits that ended in a timeout: 284, 64.7 h (one background wait that never matched ran 13 h).
- Within-agent failure odds Monitor vs until-loop 0.06 and background vs foreground 0.03 are definitional (a detached call cannot hit the cap), so they are not cited as evidence.
- The §9 prose rule did not change behaviour: foreground waits hitting the cap were 0.28 % of Bash calls before it and 0.39 % after.

## §11 (owner rule, adversarially reviewed 2026-10-07)
**Source:** `~/.claude/CLAUDE.md` §11 "Tool use, measured".
- The Bash default is 120 s. 218 of 257 foreground-wait cap hits ran ≥ 590 s because the agent raised its own `timeout`; a foreground `timeout` above 120000 is a defect to justify in the call description.
- Every wait terminates on failure and on a deadline, not only on success: one background `until` loop ran 13 h.
- A cap hit is blocked time, not a dead command (TOOL-009): 245 of 257 wait timeouts kept running in the background.
- Prose alone did not change the habit, so a PreToolUse hook is on trial (`tools/hooks/fg-wait-guard.sh`, approved 2026-10-07, pending the owner's registration). It is an experiment with success criteria in §11, not a playbook rule.
