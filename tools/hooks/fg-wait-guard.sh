#!/bin/sh
# PreToolUse guard for Bash (experiment approved 2026-10-07; see ~/.claude/CLAUDE.md §11).
# Denies ONLY: run_in_background false/absent AND timeout >= 300000 AND the command's first
# statement is an until/while loop containing `sleep`. Everything else, and any parse problem,
# is allowed (fail-open). Kill switch: CLAUDE_HOOK_FG_WAIT_OFF=1. One JSONL line per decision
# (schema fg-wait-guard/2: ts with UTC offset, cwd with $HOME as ~; the log rotates to
# fg-wait.<date>.jsonl above 5 MB). The log holds decisions only, never outcomes.
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
        import datetime
        now = datetime.datetime.now().astimezone()
        home = os.path.expanduser("~")
        cwd = d.get("cwd")
        if isinstance(cwd, str) and home and (cwd == home or cwd.startswith(home + os.sep)):
            cwd = "~" + cwd[len(home):]
        os.makedirs(log_dir, exist_ok=True)
        log = os.path.join(log_dir, "fg-wait.jsonl")
        try:
            if os.path.getsize(log) > 5 * 1024 * 1024:
                dest = os.path.join(log_dir, "fg-wait.%s.jsonl" % now.strftime("%Y-%m-%d"))
                n = 1
                while os.path.exists(dest):
                    n += 1
                    dest = os.path.join(log_dir, "fg-wait.%s-%d.jsonl" % (now.strftime("%Y-%m-%d"), n))
                os.rename(log, dest)
        except OSError:
            pass
        with open(log, "a") as f:
            f.write(json.dumps({"schema": "fg-wait-guard/2", "ts": now.isoformat(timespec="seconds"),
                "cwd": cwd, "decision": "deny" if deny else "allow", "timeout": to, "bg": bg,
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
