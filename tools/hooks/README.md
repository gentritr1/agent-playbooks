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

Judged per §11 of the global CLAUDE.md after 30 days: foreground Bash calls ≥300 s per 1,000 calls down ≥50 %
in arrows-game and geoguesser, a flat workaround detector, zsh `=` failures as the null. Remove it otherwise.
