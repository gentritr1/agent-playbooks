# Waits

**Source:** `~/.claude/CLAUDE.md` §9 (measured 2026-10-05 over 123k tool calls, 2026-06-24..10-05); arrows-game `docs/process/speed-audit-2026-10-07.md` (E13, "The 15 slowest single calls"); arrows-game memory `shared-host-contention.md` (2026-09-29 orphaned loops), `re-ceiling-gotchas.md`, `w5-art-batch-gotchas.md`, `polish-t11-gate-gotchas.md`.

- Global: 219 Bash calls ran into the 10-min cap (37 h), every one in the foreground; the same loops run in the background cost ~0. Fresh-browser screenshot harnesses ran 30 s–2.6 min each; 24 of 50 harnesses launched a fresh browser, 21 used fixed sleeps, 0 reused one.
- arrows-game helpers: 605 foreground wait loops, 142 hit the cap and were re-issued; all 15 slowest calls were capped foreground waits (601–644 s). Re-issuing costs a turn at ~280k context (E13 estimate ~0.4 h model time).
- 2026-09-29: seven background loops (`until ! pgrep -f "loopps.mjs"` and similar) ran ~42 h after their targets finished, because `pgrep -f NAME` matches the loop's own shell command line. The controller could not kill them; the owner had to.
- POLISH-T11: a `nohup`/`&` waiter survived although `ps | grep` missed it, so two chains drove the device at once; use background runs only and check the PID tree for duplicates.
- Recommended form (E13): `until [ -f DONE ] || [ -f FAILED ] || ! kill -0 $PID; do sleep 5; done`, run in the background.
