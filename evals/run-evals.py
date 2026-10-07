#!/usr/bin/env python3
"""Model-upgrade eval harness for the playbooks (python3 stdlib only). It never starts a model session.

usage:
  python3 evals/run-evals.py plan --current MODEL [--candidate MODEL] [--runs 3] [--max-cost-usd 40]
      print the exact commands: a throwaway worktree, then `claude plugin eval` per model
      (with-plugin and no-plugin arms come from --ablation with-without).
  python3 evals/run-evals.py cases
      list the cases, their tags (skills and rule ids) and grader types.
  python3 evals/run-evals.py decide METRICS.csv
      apply the decision rule to per-run metrics and print KEEP / KEEP-WATCH / TRIM / RETIRE per case,
      with the rule ids each case covers.

METRICS.csv columns: model,role,arm,case,rep,gate_pass,tokens,tool_calls,tool_errors,wall_s,owner_defects
  role: current | candidate     arm: with | without | with2     gate_pass: 0..1 (the case score)
  with2 is a second, independent with-plugin arm (same model, same case): the with-vs-with null.
Converting `aggregate-result.json` into this CSV is a manual step until the first real run shows its schema.

Decision rule (per model role and case; replicated runs only, one-shot wins do not count):
  pair reps by index; wins = reps where with > without, losses = reps where without > with.
  IMPROVES  wins >= 2 and losses == 0          WORSENS  losses >= 2 and wins == 0
  effect = mean(with) - mean(without); null spread = |mean(with) - mean(with2)|.
  An IMPROVES or WORSENS whose |effect| does not exceed the null spread is NO-EFFECT ("within null").
  otherwise NO-EFFECT. Fewer than 3 reps in with, without or with2: INSUFFICIENT (decide nothing).
  overhead = median tokens with / median tokens without - 1.
  current model:   IMPROVES -> KEEP; WORSENS -> RETIRE; NO-EFFECT -> TRIM if overhead > 10 %, else KEEP-WATCH.
  candidate model: WORSENS -> RETIRE (the rule makes the newer model worse); otherwise as for current.
  Either model: more owner-visible defects with the plugin than without -> RETIRE.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = HERE / "cases"
TOKEN_OVERHEAD_LIMIT = 0.10


def case_tags() -> dict[str, list[str]]:
    tags = {}
    for case in sorted(CASES.glob("*/case.yaml")):
        m = re.search(r"^tags:\s*\[(.*)\]\s*$", case.read_text(encoding="utf-8"), re.M)
        tags[case.parent.name] = [t.strip().strip('"\'') for t in m.group(1).split(",")] if m else []
    return tags


def cmd_cases(_: argparse.Namespace) -> int:
    for name, tags in case_tags().items():
        text = (CASES / name / "case.yaml").read_text(encoding="utf-8")
        graders = re.findall(r"^\s+type:\s*(\S+)", text, re.M)
        print(f"{name:28} {' '.join(tags):60} graders: {','.join(graders)}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    stamp = dt.date.today().isoformat()
    wt = f"$TMPDIR/agent-playbooks-eval-{stamp}"
    print("# 1. Throwaway worktree of the plugin at the commit under test (results stay out of the main tree)")
    print(f"git -C {ROOT} worktree add --detach {wt} HEAD")
    print(f"cd {wt} && python3 tools/lint-playbooks.py && python3 -m unittest discover -s tests")
    models = [("current", args.current)] + ([("candidate", args.candidate)] if args.candidate else [])
    print("# 2. One eval per model. Each case runs with and without the plugin (--ablation with-without),")
    print(f"#    {args.runs} runs per arm; scaffolds create a fresh temp workspace per run.")
    for role, model in models:
        out = f"evals/runs/{stamp}-{role}-{model}"
        print(f"claude plugin eval . --model {model} --runs {args.runs} --ablation with-without \\\n"
              f"  --scaffold --allow-tools Bash Write Edit --trust-plugin --no-publish \\\n"
              f"  --max-cost-usd {args.max_cost_usd} --output-dir {out} --json {out}/result.json")
        print(f"# with-vs-with null arm (rows become arm=with2): a second, independent with-plugin run")
        print(f"claude plugin eval . --model {model} --runs {args.runs} --ablation none \\\n"
              f"  --scaffold --allow-tools Bash Write Edit --trust-plugin --no-publish \\\n"
              f"  --max-cost-usd {args.max_cost_usd} --output-dir {out}-null --json {out}-null/result.json")
    print("# 3. Convert each result.json into METRICS.csv rows (see the module docstring), then:")
    print("python3 evals/run-evals.py decide evals/runs/METRICS.csv")
    print("# 4. Record the verdicts in CHANGELOG.md; move RETIRE rules to retired/ with the numbers.")
    print(f"git -C {ROOT} worktree remove {wt}   # after copying evals/runs/ out")
    return 0


def paired(with_runs: dict[int, float], without_runs: dict[int, float]) -> tuple[int, int]:
    wins = losses = 0
    for rep in sorted(set(with_runs) & set(without_runs)):
        if with_runs[rep] > without_runs[rep]:
            wins += 1
        elif with_runs[rep] < without_runs[rep]:
            losses += 1
    return wins, losses


def decide(rows: list[dict]) -> list[tuple[str, str, str, str]]:
    """Return (role, model, case, verdict-with-reason) for every (role, case) in the rows."""
    groups: dict[tuple[str, str, str], dict[str, dict[int, dict]]] = defaultdict(lambda: {"with": {}, "without": {}, "with2": {}})
    for r in rows:
        groups[(r["role"], r["model"], r["case"])][r["arm"]][int(r["rep"])] = r
    out = []
    for (role, model, case), arms in sorted(groups.items()):
        w, wo, w2 = arms["with"], arms["without"], arms["with2"]
        if len(w) < 3 or len(wo) < 3 or len(w2) < 3:
            out.append((role, model, case, f"INSUFFICIENT (reps with={len(w)}, without={len(wo)}, with2={len(w2)}; "
                                           "need 3 each, with2 is the with-vs-with null)"))
            continue
        score_w = {k: float(v["gate_pass"]) for k, v in w.items()}
        score_wo = {k: float(v["gate_pass"]) for k, v in wo.items()}
        score_w2 = {k: float(v["gate_pass"]) for k, v in w2.items()}
        wins, losses = paired(score_w, score_wo)
        size = statistics.mean(score_w.values()) - statistics.mean(score_wo.values())
        null = abs(statistics.mean(score_w.values()) - statistics.mean(score_w2.values()))
        effect = "IMPROVES" if wins >= 2 and losses == 0 else "WORSENS" if losses >= 2 and wins == 0 else "NO-EFFECT"
        within_null = effect != "NO-EFFECT" and abs(size) <= null
        if within_null:
            effect = "NO-EFFECT"
        tok_w = statistics.median(float(v["tokens"]) for v in w.values())
        tok_wo = statistics.median(float(v["tokens"]) for v in wo.values())
        overhead = tok_w / tok_wo - 1 if tok_wo else 0.0
        defects_w = sum(int(v.get("owner_defects") or 0) for v in w.values())
        defects_wo = sum(int(v.get("owner_defects") or 0) for v in wo.values())
        if defects_w > defects_wo:
            verdict = "RETIRE"
        elif effect == "IMPROVES":
            verdict = "KEEP"
        elif effect == "WORSENS":
            verdict = "RETIRE"
        else:
            verdict = "TRIM" if overhead > TOKEN_OVERHEAD_LIMIT else "KEEP-WATCH"
        reason = (f"{effect}{' (within null)' if within_null else ''}: wins {wins}, losses {losses}; "
                  f"pass {statistics.mean(score_w.values()):.2f} vs {statistics.mean(score_wo.values()):.2f}; "
                  f"effect {size:+.2f} vs null {null:.2f}; tokens {overhead:+.0%}; defects {defects_w} vs {defects_wo}")
        out.append((role, model, case, f"{verdict} ({reason})"))
    return out


def cmd_decide(args: argparse.Namespace) -> int:
    with open(args.metrics, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    tags = case_tags()
    for role, model, case, verdict in decide(rows):
        rules = " ".join(t.split(":", 1)[1] for t in tags.get(case, []) if t.startswith("rule:"))
        print(f"{role:9} {model:22} {case:28} {verdict}  rules: {rules or '-'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Model-upgrade eval harness (prints commands; never runs a model).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--current", required=True)
    p.add_argument("--candidate")
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--max-cost-usd", type=float, default=40.0)
    p.set_defaults(func=cmd_plan)
    c = sub.add_parser("cases")
    c.set_defaults(func=cmd_cases)
    d = sub.add_parser("decide")
    d.add_argument("metrics")
    d.set_defaults(func=cmd_decide)
    args = ap.parse_args(argv)
    if getattr(args, "runs", 3) < 3:
        print("error: --runs must be >= 3 (one-shot wins do not count)", file=sys.stderr)
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
