#!/usr/bin/env python3
"""Format + staleness lint for the playbooks (python3 stdlib only).

usage: python3 tools/lint-playbooks.py [ROOT] [--today YYYY-MM-DD] [--max-age-days 90]

Exit 1 (FAIL) on:
  format   - a rule missing any field; a Source id that differs from its heading, is malformed,
             is duplicated across skills, or reuses a retired id (retired/*.md);
           - Kind not invariant|fact|heuristic; an invariant without `why:`; a heuristic without
             `goal:`, an `override:` clause and `expires: YYYY-MM-DD` no more than 90 days after
             its last_validated;
           - Confidence not VERIFIED/INFERRED (INFERRED must carry a reason);
  evidence - an Evidence field without a link into evidence/; any dangling relative link; an
             evidence file with no `Source:` line;
  dates    - a malformed or future last_validated / expires;
  budget   - a description over 60 words, all descriptions together over 600 tokens, a SKILL.md
             body over 1,500 tokens (tokens estimated as chars/4);
  skill    - frontmatter name != directory, no description, no "## Not covered" section;
  hygiene  - an unparsable plugin manifest; text that looks like a secret or an e-mail address.
Warn (exit 0) on: a fact/heuristic whose last_validated is older than --max-age-days, an expired
heuristic, more than 15 rules in one skill, an evidence file no rule links to.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playbook_rules import (  # noqa: E402
    FIELDS, KINDS, LINK, RULE_ID, parse_rules, skill_dirs, split_frontmatter)

SECRET_PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "e-mail address"),
    (re.compile(r"\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{8,}"), "API key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"postgres(?:ql)?://[^\s:/]+:[^\s@/]+@"), "database URL with password"),
    (re.compile(r"ca-app-pub-\d{16}[~/]\d{10}"), "AdMob production id"),
]
MAX_RULES = 15
MAX_DESC_WORDS = 60
MAX_DESC_TOKENS_TOTAL = 600
MAX_BODY_TOKENS = 1500
HEURISTIC_MAX_DAYS = 90
RETIRED_ID = re.compile(r"^\*\*Retired id:\*\*\s*([A-Z]{2,6}-\d{3})", re.M)


def est_tokens(text: str) -> int:
    """Token estimate used for every budget: characters / 4, rounded up."""
    return -(-len(text) // 4)


def parse_date(stamp: str | None) -> dt.date | None:
    if not stamp or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", stamp):
        return None
    try:
        return dt.date.fromisoformat(stamp)
    except ValueError:
        return None


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.desc_tokens_total = 0

    def fail(self, where: str, msg: str) -> None:
        self.errors.append(f"FAIL {where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"WARN {where}: {msg}")


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def check_links(md: Path, root: Path, rep: Report) -> set[Path]:
    """Fail on dangling relative links; return the resolved targets."""
    targets: set[Path] = set()
    in_fence = False
    for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for target in LINK.findall(line):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            target_path = (md.parent / target.split("#", 1)[0]).resolve()
            if not target_path.exists():
                rep.fail(f"{rel(md, root)}:{n}", f"dangling link -> {target}")
            else:
                targets.add(target_path)
    return targets


def check_secrets(path: Path, root: Path, rep: Report) -> None:
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(line):
                rep.fail(f"{rel(path, root)}:{n}", f"looks like a {label}; playbooks carry no secrets or personal data")


def check_rule(rule, skill: Path, root: Path, today: dt.date, max_age: int, rep: Report) -> None:
    where = f"{rel(rule.path, root)}:{rule.line} {rule.rule_id}"
    for name in FIELDS:
        if not rule.fields.get(name):
            rep.fail(where, f"missing field '{name}'")
    source = rule.fields.get("Source", "").strip("` ")
    if source and source != rule.rule_id:
        rep.fail(where, f"Source '{source}' differs from heading id '{rule.rule_id}'")
    if source and not RULE_ID.match(source):
        rep.fail(where, f"Source '{source}' is not a stable id like ANDR-007")
    conf = rule.fields.get("Confidence", "")
    if conf:
        word = conf.split()[0].strip("*`.,;:")
        if word not in ("VERIFIED", "INFERRED"):
            rep.fail(where, f"Confidence must start with VERIFIED or INFERRED, got '{word}'")
        elif word == "INFERRED" and len(conf.split()) < 3:
            rep.fail(where, "INFERRED needs a reason after it (why it is unmeasured)")
    evidence = rule.fields.get("Evidence", "")
    if evidence:
        links = [t for t in LINK.findall(evidence) if t.startswith("evidence/")]
        if not links:
            rep.fail(where, "Evidence has no link into evidence/")
        for t in links:
            if not (skill / t.split("#", 1)[0]).is_file():
                rep.fail(where, f"dangling evidence link -> {t}")
    kind_text = rule.fields.get("Kind", "")
    validated = parse_date(rule.last_validated())
    if kind_text:
        if rule.kind not in KINDS:
            rep.fail(where, f"Kind must be one of {', '.join(KINDS)}, got '{rule.kind}'")
        elif rule.kind == "invariant" and "why:" not in kind_text:
            rep.fail(where, "invariant must state why: (the reason it never expires)")
        elif rule.kind == "heuristic":
            for needle, msg in (("goal:", "a goal: it serves"), ("override:", "an override: clause")):
                if needle not in kind_text:
                    rep.fail(where, f"heuristic needs {msg}")
            stamp = rule.expires()
            expires = parse_date(stamp)
            if stamp is None:
                rep.fail(where, "heuristic needs expires: YYYY-MM-DD")
            elif expires is None:
                rep.fail(where, f"malformed expires '{stamp}' (want YYYY-MM-DD)")
            else:
                if validated and (expires - validated).days > HEURISTIC_MAX_DAYS:
                    rep.fail(where, f"expires {stamp} is more than {HEURISTIC_MAX_DAYS} days after last_validated")
                if expires < today:
                    rep.warn(where, f"EXPIRED heuristic (expires {stamp}); re-validate or retire it")
    if rule.fields.get("Valid while"):
        stamp = rule.last_validated()
        if stamp is None:
            rep.fail(where, "Valid while has no last_validated: YYYY-MM-DD")
        elif validated is None:
            rep.fail(where, f"malformed last_validated '{stamp}' (want YYYY-MM-DD)")
        else:
            age = (today - validated).days
            if age < 0:
                rep.fail(where, f"last_validated {stamp} is in the future")
            elif age > max_age and rule.kind != "invariant":
                rep.warn(where, f"STALE: last_validated {stamp} is {age} days old (> {max_age}); "
                                "re-validate or demote before serving it as fact")


def lint(root: Path, today: dt.date, max_age: int) -> Report:
    rep = Report()
    for manifest in (root / ".claude-plugin" / "plugin.json", root / ".claude-plugin" / "marketplace.json"):
        if manifest.exists():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                if not data.get("name"):
                    rep.fail(rel(manifest, root), "missing 'name'")
            except json.JSONDecodeError as exc:
                rep.fail(rel(manifest, root), f"invalid JSON: {exc}")
    seen: dict[str, str] = {}
    retired: dict[str, str] = {}
    retired_dir = root / "retired"
    if retired_dir.is_dir():
        for doc in sorted(retired_dir.glob("*.md")):
            check_links(doc, root, rep)
            check_secrets(doc, root, rep)
            for rid in RETIRED_ID.findall(doc.read_text(encoding="utf-8")):
                retired[rid] = rel(doc, root)
    skills = skill_dirs(root)
    desc_tokens_total = 0
    if not skills:
        rep.fail(rel(root, root), "no skills/<name>/SKILL.md found")
    for skill in skills:
        md = skill / "SKILL.md"
        text = md.read_text(encoding="utf-8")
        meta, body = split_frontmatter(text)
        if meta.get("name") != skill.name:
            rep.fail(rel(md, root), f"frontmatter name '{meta.get('name')}' must equal the directory '{skill.name}'")
        desc = meta.get("description", "")
        if not desc:
            rep.fail(rel(md, root), "frontmatter has no description")
        elif len(desc) > 1024:
            rep.fail(rel(md, root), f"description is {len(desc)} chars (> 1024)")
        if len(desc.split()) > MAX_DESC_WORDS:
            rep.fail(rel(md, root), f"description is {len(desc.split())} words (> {MAX_DESC_WORDS}); "
                                    "it loads into every session, keep only triggers")
        desc_tokens_total += est_tokens(desc)
        body_tokens = est_tokens(body)
        if body_tokens > MAX_BODY_TOKENS:
            rep.fail(rel(md, root), f"body is ~{body_tokens} tokens (> {MAX_BODY_TOKENS}, chars/4); "
                                    "disclose detail into evidence/")
        if not re.search(r"^##\s+Not covered", body, re.M):
            rep.fail(rel(md, root), "no '## Not covered / defer to ...' section")
        rules = parse_rules(md)
        rule_lines = len(re.findall(r"^-\s+\*\*Rule:\*\*", re.sub(r"```.*?```", "", text, flags=re.S), re.M))
        if rule_lines != len(rules):
            rep.fail(rel(md, root), f"{rule_lines} '- **Rule:**' lines but {len(rules)} parsed rules; "
                                    "a heading must read '### PREFIX-NNN · title'")
        if len(rules) > MAX_RULES:
            rep.warn(rel(md, root), f"{len(rules)} rules inline (> {MAX_RULES}); prefer fewer, sharper rules")
        for rule in rules:
            if rule.rule_id in retired:
                rep.fail(f"{rel(md, root)}:{rule.line}", f"{rule.rule_id} is retired ({retired[rule.rule_id]}); "
                                                         "new evidence needs a new id and a CHANGELOG entry")
            if rule.rule_id in seen:
                rep.fail(f"{rel(md, root)}:{rule.line}", f"duplicate rule id {rule.rule_id} (also in {seen[rule.rule_id]})")
            else:
                seen[rule.rule_id] = rel(md, root)
            check_rule(rule, skill, root, today, max_age, rep)
        linked = check_links(md, root, rep)
        check_secrets(md, root, rep)
        evidence_dir = skill / "evidence"
        if evidence_dir.is_dir():
            for ev in sorted(evidence_dir.rglob("*")):
                if not ev.is_file():
                    continue
                check_secrets(ev, root, rep)
                if ev.suffix == ".md":
                    linked |= check_links(ev, root, rep)
                    if not re.search(r"^\*?\*?Source", ev.read_text(encoding="utf-8"), re.M):
                        rep.fail(rel(ev, root), "evidence file has no 'Source:' line naming where the data came from")
                if ev.resolve() not in linked:
                    rep.warn(rel(ev, root), "evidence file is not linked from SKILL.md")
    if desc_tokens_total > MAX_DESC_TOKENS_TOTAL:
        rep.fail("skills/*/SKILL.md", f"descriptions total ~{desc_tokens_total} tokens "
                                      f"(> {MAX_DESC_TOKENS_TOTAL}, chars/4); they load into every session")
    rep.desc_tokens_total = desc_tokens_total
    for doc in ("README.md", "CONTRIBUTING.md", "CHANGELOG.md"):
        if (root / doc).exists():
            check_links(root / doc, root, rep)
            check_secrets(root / doc, root, rep)
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for tests")
    ap.add_argument("--max-age-days", type=int, default=90)
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    rep = lint(root, today, args.max_age_days)
    n_rules = sum(len(parse_rules(s / "SKILL.md")) for s in skill_dirs(root))
    for line in rep.errors + rep.warnings:
        print(line)
    status = "FAIL" if rep.errors else "PASS"
    print(f"{status}: {len(skill_dirs(root))} skills, {n_rules} rules, "
          f"descriptions ~{rep.desc_tokens_total} tokens (chars/4), "
          f"{len(rep.errors)} errors, {len(rep.warnings)} warnings")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
