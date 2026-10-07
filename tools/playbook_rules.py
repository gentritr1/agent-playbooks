"""Shared parser for playbook rules (python3 stdlib only).

A rule is a level-3 heading `### <ID> · <title>` followed by seven bullet fields:
Rule, Kind, Evidence, Confidence, Gate, Valid while, Source. See CONTRIBUTING.md for the format.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

RULE_ID = re.compile(r"^[A-Z]{2,6}-\d{3}$")
HEADING = re.compile(r"^###\s+([A-Z]{2,6}-\d{3})\s+·\s+(.+?)\s*$")
FIELD = re.compile(r"^-\s+\*\*(Rule|Kind|Evidence|Confidence|Gate|Valid while|Source):\*\*\s*(.*)$")
FIELDS = ("Rule", "Kind", "Evidence", "Confidence", "Gate", "Valid while", "Source")
KINDS = ("invariant", "fact", "heuristic")
EXPIRES = re.compile(r"expires:\s*(\S+)")
LAST_VALIDATED = re.compile(r"last_validated:\s*(\S+)")
# `name@version` tokens inside backticks in a Valid-while line, e.g. `react-native@0.86`.
VERSION_TOKEN = re.compile(r"`([@A-Za-z0-9_.\-/]+)@([0-9][0-9A-Za-z.\-]*)`")
# `ctx:<name>` tokens inside backticks, e.g. `ctx:vercel`.
CONTEXT_TOKEN = re.compile(r"`ctx:([a-z0-9\-]+)`")
LINK = re.compile(r"\]\(([^)\s]+)\)")


@dataclass
class Rule:
    rule_id: str
    title: str
    path: Path
    line: int
    fields: dict = field(default_factory=dict)

    @property
    def valid_while(self) -> str:
        return self.fields.get("Valid while", "")

    def version_tokens(self) -> list[tuple[str, str]]:
        return VERSION_TOKEN.findall(self.valid_while)

    def context_tokens(self) -> list[str]:
        return CONTEXT_TOKEN.findall(self.valid_while)

    @property
    def kind(self) -> str:
        words = self.fields.get("Kind", "").split()
        return words[0].strip("*`.,;:—-").lower() if words else ""

    def expires(self) -> str | None:
        m = EXPIRES.search(self.fields.get("Kind", ""))
        return m.group(1).strip("`.,;") if m else None

    def last_validated(self) -> str | None:
        m = LAST_VALIDATED.search(self.valid_while)
        return m.group(1).strip("`.,;") if m else None


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict of top-level `key: value` lines, body). Empty dict if absent."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    meta = {}
    for raw in text[4:end].splitlines():
        if ":" in raw and not raw.startswith((" ", "\t")):
            key, _, value = raw.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, text[end + 4:]


def parse_rules(path: Path) -> list[Rule]:
    """Parse every rule block in a SKILL.md. A rule ends at the next heading of level <= 3."""
    rules: list[Rule] = []
    current: Rule | None = None
    last_field: str | None = None
    in_fence = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if m:
            current = Rule(m.group(1), m.group(2), path, n)
            rules.append(current)
            last_field = None
            continue
        if line.startswith("#") and len(line) - len(line.lstrip("#")) <= 3:
            current = None
            continue
        if current is None:
            continue
        f = FIELD.match(line)
        if f:
            last_field = f.group(1)
            current.fields[last_field] = f.group(2).strip()
        elif last_field and line.startswith("  ") and line.strip():
            current.fields[last_field] += " " + line.strip()
    return rules


def skill_dirs(root: Path) -> list[Path]:
    skills = root / "skills"
    return sorted(p for p in skills.iterdir() if (p / "SKILL.md").is_file()) if skills.is_dir() else []
