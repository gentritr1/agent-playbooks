# fg-wait-guard (experiment, owner-approved 2026-10-07)

A PreToolUse hook for Bash that denies only foreground `until`/`while … sleep` waits with `timeout` ≥ 300000
and asks the agent to resend the command with `run_in_background: true`. It fails open, honours the kill switch
`CLAUDE_HOOK_FG_WAIT_OFF=1`, and logs one line per decision to `~/.claude/process-metrics/hooks/fg-wait.jsonl`.

Agents may not register hooks themselves; the owner adds this to `~/.claude/settings.json`:

```json
"hooks": {
  "PreToolUse": [
    { "matcher": "Bash",
      "hooks": [ { "type": "command",
                   "command": "sh ~/.claude/plugins/agent-playbooks-hooks/fg-wait-guard.sh" } ] }
  ]
}
```
(Point `command` at wherever this script lives, e.g. this repo's checkout.)

## Log

One line per decision in `~/.claude/process-metrics/hooks/fg-wait.jsonl`, schema `fg-wait-guard/2`: `ts` is ISO 8601
with the UTC offset, `cwd` has the home directory written as `~`, plus `decision`, `timeout`, `bg`, `loop` and a
16-hex `cmd_sha` (never the command text). Above 5 MB the log is renamed to `fg-wait.<date>.jsonl` and a new one starts.
Lines written before 2026-10-07 12:12 are schema `fg-wait-guard/1` (naive local `ts`, absolute `cwd`).

The log records decisions, never outcomes (whether the agent then backgrounded the command, waited another way, or
gave up), so it cannot judge the experiment.

## Judging

Per §11 of the global CLAUDE.md, on 2026-11-06, from transcripts:
`~/.claude/process-metrics/bin/harness-audit --judge-fg-wait`. It compares the post window with the frozen baseline
`~/.claude/process-metrics/reports/fg-wait-baseline-2026-10-07.{json,md}` (2026-09-07 .. 2026-10-07 11:45) under the
pre-registered rule FG-WAIT-R1 stored in that file: foreground Bash calls ≥ 300 s per 1,000 Bash calls down ≥ 50 % in
both arrows-game and geoguesser-app and beyond count noise, the workaround detector flat, zsh `=` failures (the null)
flat. A rising workaround detector means remove the hook.

## Known gaps (out of scope on purpose)

The predicate is a live experiment and does not change mid-run. It leaves these legal; the §11 invariant covers them,
not the hook, and harness-audit reports them as `gap:` counts without judging them:
- `for` loops with `sleep` (`for i in $(seq 60); do …; sleep 5; done`);
- a `cd … &&` (or any other) prefix before the `until`/`while` loop, since only the first statement is checked;
- waits between 120 s and 300 s (`timeout` below 300000), which the 2-min invariant forbids but the hook allows.
