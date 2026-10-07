"""Self-tests for the eval decision rule (evals/run-evals.py). No model session is started."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUN = REPO / "evals" / "run-evals.py"
METRICS = REPO / "tests" / "fixtures" / "evals" / "metrics.csv"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(RUN), *args], capture_output=True, text=True, timeout=60)


class DecideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        res = run("decide", str(METRICS))
        assert res.returncode == 0, res.stderr
        cls.rows = {line.split()[2]: line for line in res.stdout.splitlines()}

    def test_replicated_improvement_is_kept(self) -> None:
        self.assertIn("KEEP (IMPROVES", self.rows["improves"])

    def test_one_shot_win_does_not_count_and_costly_rule_is_trimmed(self) -> None:
        self.assertIn("TRIM (NO-EFFECT: wins 1", self.rows["oneshot"])

    def test_cheap_no_effect_is_watched_not_kept(self) -> None:
        self.assertIn("KEEP-WATCH", self.rows["noeffect-cheap"])

    def test_rule_that_hurts_a_newer_model_is_retired(self) -> None:
        self.assertIn("RETIRE (WORSENS", self.rows["worse-new-model"])

    def test_owner_visible_defect_retires_even_when_scores_improve(self) -> None:
        self.assertIn("RETIRE (IMPROVES", self.rows["defects"])

    def test_fewer_than_three_reps_decides_nothing(self) -> None:
        self.assertIn("INSUFFICIENT", self.rows["short"])


class PlanTests(unittest.TestCase):
    def test_plan_prints_both_models_and_never_runs(self) -> None:
        res = run("plan", "--current", "model-a", "--candidate", "model-b")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(res.stdout.count("claude plugin eval ."), 2)
        self.assertIn("--ablation with-without", res.stdout)
        self.assertIn("worktree add", res.stdout)

    def test_single_run_is_refused(self) -> None:
        self.assertEqual(run("plan", "--current", "m", "--runs", "1").returncode, 2)

    def test_every_case_is_tagged_with_a_skill_and_a_live_rule(self) -> None:
        res = run("cases")
        lines = res.stdout.strip().splitlines()
        self.assertGreaterEqual(len(lines), 6)
        rule_ids = set()
        for skill in (REPO / "skills").iterdir():
            text = (skill / "SKILL.md").read_text() if (skill / "SKILL.md").exists() else ""
            rule_ids |= {line.split()[1] for line in text.splitlines() if line.startswith("### ")}
        for line in lines:
            self.assertIn("skill:", line)
            for tag in line.split():
                if tag.startswith("rule:"):
                    self.assertIn(tag[5:], rule_ids, f"{line.split()[0]} tags a missing rule {tag}")


if __name__ == "__main__":
    unittest.main()
