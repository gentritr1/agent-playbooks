#!/bin/sh
# PreToolUse guard for Bash (experiment approved 2026-10-07; see ~/.claude/CLAUDE.md §11).
# Denies ONLY: run_in_background false/absent AND timeout >= 300000 AND the command's first
# statement is an until/while loop containing `sleep`. Everything else, and any parse problem,
# is allowed (fail-open). Kill switch: CLAUDE_HOOK_FG_WAIT_OFF=1. One JSONL line per decision.
[ "${CLAUDE_HOOK_FG_WAIT_OFF:-0}" = "1" ] && exit 0
LOG_DIR="${HOME}/.claude/process-metrics/hooks"; export LOG_DIR
input=$(cat) || exit 0
printf '%s' "$input" | python3 -c '
import json, os, sys, time, re, hashlib
try:
    d = json.load(sys.stdin)
    if d.get("tool_name") != "Bash":
        sys.exit(0)
    ti = d.get("tool_input") or {}
    cmd = ti.get("command") or ""
    bg = bool(ti.get("run_in_background"))
    to = ti.get("timeout")
    to = int(to) if isinstance(to, (int, float)) else 0
    first = cmd.lstrip()
    loop = re.match(r"(until|while)\b", first) is not None and re.search(r"\bsleep\b", first) is not None
    deny = (not bg) and to >= 300000 and loop
    log_dir = os.environ.get("LOG_DIR")
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "fg-wait.jsonl"), "a") as f:
            f.write(json.dumps({"schema": "fg-wait-guard/1", "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "cwd": d.get("cwd"), "decision": "deny" if deny else "allow", "timeout": to, "bg": bg,
                "loop": loop, "cmd_sha": hashlib.sha256(cmd.encode()).hexdigest()[:16]}) + "\n")
    except Exception:
        pass
    if deny:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Resend this exact command with run_in_background: true; you will be notified when it exits."}}))
except Exception:
    pass
sys.exit(0)
'
exit 0
