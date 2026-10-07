"""Self-tests for tools/hooks/fg-wait-guard.sh (stdlib unittest; runs the real script under a temp HOME).

The deny predicate is a live experiment (~/.claude/CLAUDE.md §11) and must not drift: the decision table below
is the predicate's contract. Logging changes (cwd as ~, ISO ts with offset, 5 MB rotation) are tested beside it.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "tools" / "hooks" / "fg-wait-guard.sh"
LOOP = "until [ -f DONE ]; do sleep 5; done"

# (tool_input, expected decision). Deny = not background AND timeout >= 300000 AND first statement until/while with sleep.
DECISIONS = [
    ({"command": LOOP, "timeout": 300000}, "deny"),
    ({"command": "while ! grep -q Ready log; do sleep 1; done", "timeout": 600000}, "deny"),
    ({"command": "  until x; do sleep 1; done", "timeout": 600000, "run_in_background": False}, "deny"),
    ({"command": LOOP, "timeout": 299999}, "allow"),
    ({"command": LOOP}, "allow"),
    ({"command": LOOP, "timeout": 600000, "run_in_background": True}, "allow"),
    ({"command": "for i in 1 2 3; do sleep 5; done", "timeout": 600000}, "allow"),          # known gap, on purpose
    ({"command": "cd app && " + LOOP, "timeout": 600000}, "allow"),                          # known gap, on purpose
    ({"command": "until [ -f DONE ]; do :; done", "timeout": 600000}, "allow"),              # no sleep
    ({"command": "npx jest", "timeout": 600000}, "allow"),
]


class HookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.home = Path(tempfile.mkdtemp())
        self.log = self.home / ".claude" / "process-metrics" / "hooks" / "fg-wait.jsonl"

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.home)

    def call(self, payload, env_extra=None) -> subprocess.CompletedProcess:
        env = dict(os.environ, HOME=str(self.home))
        env.pop("CLAUDE_HOOK_FG_WAIT_OFF", None)
        env.update(env_extra or {})
        data = payload if isinstance(payload, str) else json.dumps(payload)
        return subprocess.run(["sh", str(HOOK)], input=data, capture_output=True, text=True, env=env, timeout=30)

    def lines(self) -> list[dict]:
        return [json.loads(x) for x in self.log.read_text().splitlines()]

    def test_decision_table_is_unchanged(self) -> None:
        for ti, want in DECISIONS:
            res = self.call({"tool_name": "Bash", "tool_input": ti, "cwd": "/tmp"})
            self.assertEqual(res.returncode, 0)
            got = "deny" if '"permissionDecision": "deny"' in res.stdout else "allow"
            self.assertEqual(got, want, ti)
        self.assertEqual([x["decision"] for x in self.lines()], [w for _, w in DECISIONS])

    def test_non_bash_and_garbage_fail_open_silently(self) -> None:
        for payload in ({"tool_name": "Read", "tool_input": {"command": LOOP, "timeout": 600000}}, "not json", ""):
            res = self.call(payload)
            self.assertEqual((res.returncode, res.stdout), (0, ""))

    def test_kill_switch(self) -> None:
        res = self.call({"tool_name": "Bash", "tool_input": {"command": LOOP, "timeout": 600000}},
                        {"CLAUDE_HOOK_FG_WAIT_OFF": "1"})
        self.assertEqual((res.returncode, res.stdout), (0, ""))
        self.assertFalse(self.log.exists())

    def test_log_maps_home_to_tilde_and_ts_has_offset(self) -> None:
        self.call({"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": str(self.home / "proj")})
        self.call({"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": "/opt/elsewhere"})
        a, b = self.lines()
        self.assertEqual(a["cwd"], "~/proj")
        self.assertEqual(b["cwd"], "/opt/elsewhere")
        self.assertEqual(a["schema"], "fg-wait-guard/2")
        self.assertIsNotNone(dt.datetime.fromisoformat(a["ts"]).utcoffset())
        self.assertNotIn(str(self.home), self.log.read_text())

    def test_log_rotates_above_5_mb(self) -> None:
        self.log.parent.mkdir(parents=True)
        self.log.write_text("x" * (5 * 1024 * 1024 + 1))
        self.call({"tool_name": "Bash", "tool_input": {"command": "ls"}})
        rotated = sorted(p.name for p in self.log.parent.glob("fg-wait.*.jsonl"))
        self.assertEqual(len(rotated), 1, rotated)
        self.assertRegex(rotated[0], r"^fg-wait\.\d{4}-\d{2}-\d{2}\.jsonl$")
        self.assertEqual(len(self.lines()), 1)

    def test_small_log_does_not_rotate(self) -> None:
        for _ in range(3):
            self.call({"tool_name": "Bash", "tool_input": {"command": "ls"}})
        self.assertEqual(list(self.log.parent.glob("fg-wait.*.jsonl")), [])
        self.assertEqual(len(self.lines()), 3)


if __name__ == "__main__":
    unittest.main()
