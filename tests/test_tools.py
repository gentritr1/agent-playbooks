"""Self-tests for tools/lint-playbooks.py and tools/check-applicability.py (stdlib unittest).

Run: python3 -m unittest discover -s tests -v

Every failing check has a negative control: the good fixture passes, then one mutation of it
must fail (or warn) for the stated reason. A lint that cannot fail proves nothing.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIX = REPO / "tests" / "fixtures"
LINT = REPO / "tools" / "lint-playbooks.py"
APPLY = REPO / "tools" / "check-applicability.py"
TODAY = "2026-10-07"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, timeout=60)


class LintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "pb"
        shutil.copytree(FIX / "good", self.root)
        self.skill = self.root / "skills" / "demo-skill" / "SKILL.md"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def lint(self, today: str = TODAY, *extra: str) -> subprocess.CompletedProcess:
        return run(str(LINT), str(self.root), "--today", today, "--no-claude", *extra)

    def lint_with_fake_claude(self, stdout: str) -> subprocess.CompletedProcess:
        bindir = self.tmp / "bin"
        bindir.mkdir(exist_ok=True)
        fake = bindir / "claude"
        fake.write_text("#!/bin/sh\nprintf '%s\\n' '" + stdout.replace("\n", "' '") + "'\n")  # builtins only: PATH holds just the fake
        fake.chmod(0o755)
        return subprocess.run([sys.executable, str(LINT), str(self.root), "--today", TODAY], capture_output=True,
                              text=True, timeout=60, env=dict(os.environ, PATH=str(bindir)))

    def mutate(self, old: str, new: str, path: Path | None = None) -> None:
        path = path or self.skill
        text = path.read_text()
        self.assertIn(old, text, "fixture drifted: mutation target missing")
        path.write_text(text.replace(old, new, 1))

    def assertFails(self, needle: str) -> None:
        res = self.lint()
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn(needle, res.stdout)

    # positive control
    def test_good_fixture_passes(self) -> None:
        res = self.lint()
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("PASS: 1 skills, 3 rules", res.stdout)

    # format
    def test_missing_field_fails(self) -> None:
        self.mutate("- **Gate:** `grep -L -- '-s ' scripts/*.sh` prints nothing\n", "")
        self.assertFails("missing field 'Gate'")

    def test_malformed_heading_cannot_hide_a_rule(self) -> None:
        self.mutate("### DEMO-002 · Build", "### DEMO-002 - Build")
        self.assertFails("parsed rules")

    def test_duplicate_id_fails(self) -> None:
        self.mutate("### DEMO-002 · Build", "### DEMO-001 · Build")
        self.mutate("- **Source:** DEMO-002", "- **Source:** DEMO-001")
        self.assertFails("duplicate rule id DEMO-001")

    def test_source_must_match_heading(self) -> None:
        self.mutate("- **Source:** DEMO-002", "- **Source:** DEMO-012")
        self.assertFails("differs from heading id")

    def test_retired_id_cannot_return(self) -> None:
        self.mutate("### DEMO-002 · Build", "### DEMO-900 · Build")
        self.mutate("- **Source:** DEMO-002", "- **Source:** DEMO-900")
        self.assertFails("DEMO-900 is retired")

    def test_bad_confidence_fails(self) -> None:
        self.mutate("- **Confidence:** VERIFIED\n- **Gate:** `unzip", "- **Confidence:** PROBABLY\n- **Gate:** `unzip")
        self.assertFails("Confidence must start with VERIFIED or INFERRED")

    def test_inferred_needs_reason(self) -> None:
        self.mutate("INFERRED — byte-identity proof not run yet", "INFERRED")
        self.assertFails("INFERRED needs a reason")

    # kinds
    def test_unknown_kind_fails(self) -> None:
        self.mutate("- **Kind:** fact —", "- **Kind:** tip —")
        self.assertFails("Kind must be one of")

    def test_invariant_needs_why(self) -> None:
        self.mutate("invariant — why: a second", "invariant — a second")
        self.assertFails("invariant must state why:")

    def test_heuristic_needs_goal(self) -> None:
        self.mutate("goal: shorter", "aim: shorter")
        self.assertFails("heuristic needs a goal:")

    def test_heuristic_needs_override(self) -> None:
        self.mutate("override: stronger case evidence, stated in the report; ", "")
        self.assertFails("heuristic needs an override: clause")

    def test_heuristic_needs_expiry(self) -> None:
        self.mutate("; expires: 2026-12-30", "")
        self.assertFails("heuristic needs expires:")

    def test_heuristic_expiry_capped_at_90_days(self) -> None:
        self.mutate("expires: 2026-12-30", "expires: 2027-03-01")
        self.assertFails("more than 90 days after last_validated")

    def test_expired_heuristic_warns(self) -> None:
        res = self.lint(today="2026-12-31")
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("EXPIRED heuristic", res.stdout)

    # evidence and links
    def test_dangling_evidence_link_fails(self) -> None:
        self.mutate("[ev](evidence/demo.md)\n- **Confidence:** VERIFIED\n- **Gate:** `unzip",
                    "[ev](evidence/missing.md)\n- **Confidence:** VERIFIED\n- **Gate:** `unzip")
        self.assertFails("dangling evidence link -> evidence/missing.md")

    def test_evidence_without_link_fails(self) -> None:
        self.mutate("two agents drove one device → [ev](evidence/demo.md)", "two agents drove one device")
        self.assertFails("Evidence has no link into evidence/")

    def test_evidence_file_needs_source(self) -> None:
        self.mutate("**Source:** tests/fixtures (synthetic)", "From: somewhere",
                    self.root / "skills" / "demo-skill" / "evidence" / "demo.md")
        self.assertFails("no 'Source:' line")

    # dates
    def test_stale_date_warns_but_passes(self) -> None:
        res = self.lint(today="2027-02-01")
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("STALE: last_validated 2026-10-01", res.stdout)
        self.assertNotIn("DEMO-001 STALE", res.stdout.replace(":", ""))  # invariants do not go stale

    def test_malformed_date_fails(self) -> None:
        self.mutate("`claude-code@2.1` · last_validated: 2026-10-01", "`claude-code@2.1` · last_validated: 2026-13-01")
        self.assertFails("malformed last_validated '2026-13-01'")

    def test_future_date_fails(self) -> None:
        self.mutate("`claude-code@2.1` · last_validated: 2026-10-01", "`claude-code@2.1` · last_validated: 2026-11-01")
        self.assertFails("is in the future")

    # budgets
    def test_long_description_fails(self) -> None:
        self.mutate("Use when testing the playbook lint; fixture only.", "Use when " + "word " * 61)
        self.assertFails("words (> 60)")

    def test_description_total_budget_fails(self) -> None:
        desc = "Use when " + " ".join(["internationalisation"] * 50)  # ~260 tokens, under 60 words
        for i in range(3):
            d = self.root / "skills" / f"extra-{i}"
            (d / "evidence").mkdir(parents=True)
            (d / "SKILL.md").write_text(f"---\nname: extra-{i}\ndescription: {desc}\n---\n\n## Not covered\n- x\n")
        self.assertFails("projected tokens")

    def test_listing_estimate_uses_the_rendered_line(self) -> None:
        line = "- pb:demo-skill: Use when testing the playbook lint; fixture only.\n"
        res = self.lint()
        self.assertIn(f"skill listing {len(line)} chars, ~{-(-len(line) * 10 // 28)} projected (chars/2.8)", res.stdout)
        self.assertIn("tokens (chars/4)", res.stdout)

    def test_claude_projection_over_budget_fails(self) -> None:
        res = self.lint_with_fake_claude("Projected token cost\n  Always-on:   ~701 tok   added to every session")
        self.assertEqual(res.returncode, 1, res.stdout)
        self.assertIn("always-on ~701 projected tokens > 700", res.stdout)

    def test_claude_projection_under_budget_passes(self) -> None:
        res = self.lint_with_fake_claude("  Always-on:   ~650 tok   added to every session")
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("~650 (claude plugin details)", res.stdout)

    def test_claude_projection_in_thousands_is_parsed(self) -> None:
        res = self.lint_with_fake_claude("  Always-on:   ~1.2k tok   added to every session")
        self.assertIn("always-on ~1200 projected tokens", res.stdout)

    def test_claude_projection_unreadable_warns_only(self) -> None:
        res = self.lint_with_fake_claude("something else")
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("projection unavailable", res.stdout)

    def test_body_budget_fails(self) -> None:
        self.mutate("## Not covered / defer to", "Padding paragraph. " * 400 + "\n\n## Not covered / defer to")
        self.assertFails("tokens (> 1500, chars/4)")

    # skill shape and hygiene
    def test_not_covered_section_required(self) -> None:
        self.mutate("## Not covered / defer to", "## Elsewhere")
        self.assertFails("no '## Not covered")

    def test_secret_fails(self) -> None:
        self.mutate("Pass the device serial", "Mail ops@example.com and pass the device serial")
        self.assertFails("looks like a e-mail address")

    def test_name_must_match_directory(self) -> None:
        self.mutate("name: demo-skill", "name: other-skill")
        self.assertFails("must equal the directory")


class ApplicabilityTests(unittest.TestCase):
    def check(self, project: str, today: str = TODAY, claude: str = "2.1.269") -> str:
        res = run(str(APPLY), str(FIX / project), "--playbooks", str(FIX / "good"), "--today", today,
                  "--claude-version", claude)
        self.assertEqual(res.returncode, 0, res.stderr)
        return res.stdout

    def check_with_path(self, path_dir: str) -> str:
        res = subprocess.run([sys.executable, str(APPLY), str(FIX / "project-match"), "--playbooks", str(FIX / "good"),
                              "--today", TODAY], capture_output=True, text=True, timeout=60,
                             env=dict(os.environ, PATH=path_dir))
        self.assertEqual(res.returncode, 0, res.stderr)
        return res.stdout

    def row(self, out: str, rule_id: str) -> str:
        m = re.search(rf"^{rule_id}\s.*$", out, re.M)
        self.assertIsNotNone(m, out)
        return m.group(0)

    def test_matching_project_applies(self) -> None:
        out = self.check("project-match")
        self.assertIn("APPLIES", self.row(out, "DEMO-002"))
        self.assertIn("react-native@0.85|0.86 == 0.86.3", self.row(out, "DEMO-002"))
        self.assertIn("APPLIES", self.row(out, "DEMO-001"))
        self.assertIn("ctx:android detected", self.row(out, "DEMO-001"))

    def test_installed_version_beats_declared_range(self) -> None:
        out = self.check("project-match")
        self.assertIn("0.86.3", self.row(out, "DEMO-002"))

    def test_version_mismatch_is_flagged_with_both_versions(self) -> None:
        row = self.row(self.check("project-mismatch"), "DEMO-002")
        self.assertIn("VERSION-DIFFERS", row)
        self.assertIn("rule 0.85|0.86 / project 0.87.0", row)
        self.assertIn("unverified here", row)

    def test_missing_context_is_unknown(self) -> None:
        self.assertIn("UNKNOWN", self.row(self.check("project-mismatch"), "DEMO-001"))

    def test_heuristic_expiry_reported(self) -> None:
        self.assertIn("heuristic expires 2026-12-30", self.row(self.check("project-match"), "DEMO-003"))
        self.assertIn("EXPIRED 2026-12-30", self.row(self.check("project-match", today="2027-01-02"), "DEMO-003"))

    # claude-code token: positive and negative controls
    def test_claude_code_version_matches_by_prefix(self) -> None:
        row = self.row(self.check("project-match"), "DEMO-001")
        self.assertIn("APPLIES", row)
        self.assertIn("claude-code@2.1 == 2.1.269", row)

    def test_claude_code_other_version_differs(self) -> None:
        row = self.row(self.check("project-match", claude="3.0.4"), "DEMO-001")
        self.assertIn("VERSION-DIFFERS", row)
        self.assertIn("claude-code: rule 2.1 / project 3.0.4", row)

    def test_claude_code_unknown_when_not_readable(self) -> None:
        row = self.row(self.check("project-match", claude="none"), "DEMO-001")
        self.assertIn("UNKNOWN", row)
        self.assertIn("claude-code@2.1: not found", row)

    def test_claude_code_detected_from_cli_on_path(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            fake = tmp / "claude"
            fake.write_text("#!/bin/sh\necho '2.1.300 (Claude Code)'\n")
            fake.chmod(0o755)
            self.assertIn("claude-code@2.1 == 2.1.300", self.row(self.check_with_path(str(tmp)), "DEMO-001"))
            fake.write_text("#!/bin/sh\necho '2.2.0 (Claude Code)'\n")
            self.assertIn("VERSION-DIFFERS", self.row(self.check_with_path(str(tmp)), "DEMO-001"))
            fake.unlink()
            row = self.row(self.check_with_path(str(tmp)), "DEMO-001")
            self.assertIn("UNKNOWN", row)
            self.assertIn("claude not on PATH", row)
        finally:
            shutil.rmtree(tmp)

    def test_bad_project_path_exits_2(self) -> None:
        res = run(str(APPLY), str(FIX / "does-not-exist"))
        self.assertEqual(res.returncode, 2)


if __name__ == "__main__":
    unittest.main()
