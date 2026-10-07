# agent-playbooks

Skills with data: shared, versioned practices that any Claude agent on any project can load before app or website work. Every rule carries measured evidence, a gate that proves it was followed, the conditions it was measured under, and a date after which it is no longer served as fact.

Status: v0.2.0, a private GitHub repository installed as a Claude Code plugin. See "Pending".

## What is inside

| Skill | Load it before | Rules |
|---|---|---|
| `expo-rn-apps` | Expo/RN animation, reduced motion, EXPO_PUBLIC flags, Hermes perf, dense rendering, react-native-svg | 6 |
| `android-builds-devices` | Gradle/prebuild, test APKs (arm64-only, fingerprint-gated incremental), adb and emulators, capture harnesses, shared hosts | 7 |
| `ui-motion-quality` | visual, layout or motion changes, pixel and contrast gates, recording timing, owner acceptance | 7 |
| `vercel-cost-cache` | Vercel deploys, headers, caching, static vs function, bill work | 5 |
| `data-persistence` | save or DB schema changes, Neon/Postgres URLs, timeouts, health checks | 5 |
| `testing-gates` | tests, detectors, benchmarks, A/B perf, quoted numbers | 7 |
| `store-release` | release AABs, test-ads proof, Play surfaces, store text | 6 |
| `agent-process` | delegation, waits and long commands, worktrees, merges, outward steps, speed changes | 6 |
| `tool-reliability` | file edits through the shell, zsh quoting and `find`, worktree-agent commands, repeated calls, timeouts, host-load claims, parked subagents | 7 |
| `code-and-doc-lookup` | code search, library API and version facts, trusting an index, language server or docs service | 3 |

Each skill has `SKILL.md` (the rules, inline) and `evidence/` (short extracts naming their source files). `retired/` lists rules that evidence disproved; their ids can never come back.

## How an agent uses it

1. The skill loads when its description matches the task. Read the rules; open an evidence file only when a rule is in doubt or the task touches its detail.
2. Run `python3 tools/check-applicability.py <project>`. A rule marked `VERSION-DIFFERS` or `UNKNOWN` was not measured on this project's versions: treat it as unverified here and say so. An `EXPIRED` heuristic is a hypothesis.
3. Finish against the gates. Cite rule ids in the report (e.g. "TEST-003 gate: null spread 0.08 ms, n=8 per arm").
4. A heuristic may be overridden when the case at hand has stronger evidence; the report must state the evidence. Invariants and gates are not overridden; escalate to the owner instead.

## How rules enter, change and expire

- **Enter:** a project lesson with measured evidence is promoted through the review gate in [CONTRIBUTING.md](CONTRIBUTING.md). Generic advice without our data stays out, or enters as INFERRED with the reason.
- **Change:** new evidence updates the rule and its `last_validated`; the CHANGELOG says what changed and why. Contradictions resolve to the newer, better-controlled evidence, citing both.
- **Expire:** facts and heuristics older than 90 days make the lint warn; heuristics also carry an `expires:` date at most 90 days after validation. Disproved or unhelpful rules move to `retired/` with the numbers.

## Tools

```
python3 tools/lint-playbooks.py                 # format, evidence links, dates, kinds, token budgets, secrets
python3 tools/check-applicability.py <project>  # APPLIES / VERSION-DIFFERS / UNKNOWN per rule, heuristic expiry
python3 -m unittest discover -s tests           # self-tests, with negative controls for every failing check
python3 evals/run-evals.py plan --current <model> [--candidate <model>]   # prints eval commands; runs nothing
claude plugin validate .                        # manifest check (passes; one warning: no author yet)
```

## Token budget (measured 2026-10-07)

Skill descriptions load into every session, so they are the most expensive bytes. Figures below are for v0.2.0 (10 skills).

| Measure | Descriptions, all skills | SKILL.md body, each |
|---|---|---|
| chars / 4 (the lint's estimate) | ~368 tokens (10 skills) | 947–1,489 |
| `claude --plugin-dir . plugin details agent-playbooks` projection | ~658 tokens always-on (includes names; v0.1.1: ~594) | ~1.5k–2.4k on invoke |

The lint fails above 60 words per description, 600 tokens for all descriptions, or 1,500 tokens per body, all by chars/4. Claude Code's own projection reads about 1.5× higher for bodies; see CHANGELOG RULING R3.

## How this avoids dumbing down future models

- **Kinds.** Invariants (safety, irreversibility, owner preferences, quality gates) state why and do not expire. Facts state the versions and conditions they were measured under and expire with them. Heuristics, the only "how to" rules, state the goal they serve, allow an override with stronger evidence, and expire within 90 days unless re-validated.
- **Gates over procedures.** Rules say what must be true at the end, so a smarter model can reach it its own way. Procedures remain only where the procedure is the invariant (the release recipe).
- **Staleness is visible.** The lint warns on old facts and expired heuristics; `check-applicability.py` marks rules measured on other versions as unverified here.
- **Retirement is recorded.** `retired/` keeps the reason and the reopening condition, and the lint refuses a retired id.
- **Measured, then corrected.** The eval harness in [evals/](evals/README.md) runs fixed tasks with and without the plugin on the current and any new model. Rules that do not raise the gate-pass rate, that cost tokens without benefit, or that make a newer model worse are trimmed or retired.

This cannot be proven in advance. Whether a rule helps or hinders a future model is an empirical question that only the eval harness, run with replicated runs, can answer. Until it has run, every claim of benefit in this repo is a hypothesis.

## Pending

- The first eval run (designed and stubbed; never run). 12 cases; ev11 and ev12 were added in v0.2.0.
- The `fg-wait-guard` hook ([tools/hooks](tools/hooks/README.md)) is an approved experiment that starts when the owner registers it; it is not a rule.
- TOOL-008 is re-measured after 30 days of hook data (its expiry, 2026-11-06, forces the look).
- ANDR-002's time saving is unproven on a loaded host; the bytes carry the rule.
- Claude Code projects ~658 always-on tokens, above the 600 the lint enforces by chars/4 (~368); see CHANGELOG R3.
