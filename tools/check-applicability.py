#!/usr/bin/env python3
"""Compare each rule's "Valid while" against a target project (python3 stdlib only).

usage: python3 tools/check-applicability.py <project-path> [--skill NAME] [--today YYYY-MM-DD]
                                            [--playbooks ROOT] [--only-problems]

Per rule it prints one status:
  APPLIES          every `pkg@ver` token matches the project's version prefix and every `ctx:`
                   token is detected (a rule with neither is version-free and APPLIES);
  VERSION-DIFFERS  a package is present at a different version: both versions are shown and the
                   rule must be presented as "unverified here";
  UNKNOWN          a package or context the rule names was not found in the project.
Heuristics also get their expiry: an EXPIRED heuristic is a hypothesis, not guidance.

Versions come from node_modules/<pkg>/package.json when installed (the runtime truth), else the
package.json range with ^/~ stripped; `gradle` from android/gradle/wrapper/gradle-wrapper.properties;
`node` from .nvmrc / .node-version / package.json engines. Exit 0 unless the project path is bad.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playbook_rules import parse_rules, skill_dirs  # noqa: E402


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


class Project:
    def __init__(self, root: Path) -> None:
        self.root = root
        pkg = read_json(root / "package.json")
        self.declared: dict[str, str] = {}
        for section in ("dependencies", "devDependencies", "peerDependencies"):
            self.declared.update(pkg.get(section, {}) or {})
        self.engines = pkg.get("engines", {}) or {}
        self.app = read_json(root / "app.json").get("expo", {})

    def version(self, name: str) -> tuple[str | None, str]:
        """Return (version, where it came from)."""
        if name == "gradle":
            props = self.root / "android" / "gradle" / "wrapper" / "gradle-wrapper.properties"
            if props.is_file():
                m = re.search(r"gradle-([0-9][0-9.]*)-(?:bin|all)\.zip", props.read_text(encoding="utf-8"))
                if m:
                    return m.group(1), "gradle-wrapper.properties"
            return None, "no android/gradle/wrapper"
        if name == "node":
            for f in (".nvmrc", ".node-version"):
                p = self.root / f
                if p.is_file():
                    return p.read_text(encoding="utf-8").strip().lstrip("v"), f
            if "node" in self.engines:
                return clean(self.engines["node"]), "package.json engines"
            return None, "no .nvmrc/.node-version/engines"
        if name == "expo" and self.app.get("sdkVersion"):
            return self.app["sdkVersion"], "app.json sdkVersion"
        installed = read_json(self.root / "node_modules" / name / "package.json").get("version")
        if installed:
            return installed, "node_modules"
        if name in self.declared:
            return clean(self.declared[name]), "package.json range"
        return None, "not a dependency"

    def has_context(self, ctx: str) -> bool:
        r, d = self.root, self.declared
        detectors = {
            "any": lambda: True,
            "git": lambda: (r / ".git").exists(),
            "expo": lambda: "expo" in d,
            "react-native": lambda: "react-native" in d,
            "android": lambda: (r / "android").is_dir() or "android" in self.app,
            "ios": lambda: (r / "ios").is_dir() or "ios" in self.app,
            "jest": lambda: "jest" in d or (r / "jest.config.js").exists(),
            "vercel": lambda: (r / "vercel.json").exists() or (r / ".vercel").is_dir() or "vercel" in d,
            "web": lambda: any(k in d for k in ("next", "vite", "react-dom", "astro")),
            "neon": lambda: any(k.startswith("@neondatabase/") for k in d),
            "postgres": lambda: any(k in d for k in ("pg", "postgres", "prisma", "@prisma/client", "drizzle-orm"))
                                or any(k.startswith("@neondatabase/") for k in d),
            "ads": lambda: any("ads" in k or "mediation" in k for k in d),
        }
        return detectors.get(ctx, lambda: False)()


def clean(spec: str) -> str:
    m = re.search(r"[0-9][0-9A-Za-z.\-]*", spec)
    return m.group(0) if m else spec


def prefix_matches(want: str, have: str) -> bool:
    want_parts = want.split(".")
    have_parts = re.split(r"[.\-+]", have)
    return have_parts[: len(want_parts)] == want_parts


def evaluate(rule, project: Project, today: dt.date) -> tuple[str, list[str]]:
    notes: list[str] = []
    status = "APPLIES"
    for name, want in rule.version_tokens():
        have, source = project.version(name)
        if have is None:
            status = "UNKNOWN" if status == "APPLIES" else status
            notes.append(f"{name}@{want}: not found ({source})")
        elif prefix_matches(want, have):
            notes.append(f"{name}@{want} == {have}")
        else:
            status = "VERSION-DIFFERS"
            notes.append(f"{name}: rule {want} / project {have} ({source})")
    for ctx in rule.context_tokens():
        if not project.has_context(ctx):
            status = "UNKNOWN" if status == "APPLIES" else status
            notes.append(f"ctx:{ctx} not detected")
    if not rule.version_tokens() and not rule.context_tokens():
        notes.append("version-free")
    if status == "VERSION-DIFFERS":
        notes.append("=> unverified here: re-measure before treating as fact")
    if rule.kind == "heuristic":
        stamp = rule.expires()
        try:
            left = (dt.date.fromisoformat(stamp) - today).days if stamp else None
        except ValueError:
            left = None
        if left is None:
            notes.append("heuristic: no valid expires (lint should fail)")
        elif left < 0:
            notes.append(f"EXPIRED {stamp}: a hypothesis, not guidance, until re-validated")
        else:
            notes.append(f"heuristic expires {stamp} ({left} d)")
    return status, notes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project")
    ap.add_argument("--playbooks", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--skill", help="only this skill directory name")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for tests")
    ap.add_argument("--only-problems", action="store_true", help="hide APPLIES rows")
    args = ap.parse_args(argv)
    root = Path(args.project).resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    project = Project(root)
    counts = {"APPLIES": 0, "VERSION-DIFFERS": 0, "UNKNOWN": 0}
    expired = 0
    print(f"project: {root}")
    for skill in skill_dirs(Path(args.playbooks)):
        if args.skill and skill.name != args.skill:
            continue
        for rule in parse_rules(skill / "SKILL.md"):
            status, notes = evaluate(rule, project, today)
            counts[status] += 1
            expired += any(n.startswith("EXPIRED") for n in notes)
            if args.only_problems and status == "APPLIES" and not any(n.startswith("EXPIRED") for n in notes):
                continue
            print(f"{rule.rule_id:<9} {status:<15} [{rule.kind or '?'}] {'; '.join(notes)}")
    print("summary: " + ", ".join(f"{k} {v}" for k, v in counts.items()) + f", EXPIRED heuristics {expired}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
