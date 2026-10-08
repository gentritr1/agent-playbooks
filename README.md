# agent-playbooks

Skills with data: shared, versioned practices that any Claude agent on any project can load before app or website work. Every rule carries measured evidence, a gate that proves it was followed, the conditions it was measured under, and a date after which it is no longer served as fact.

Status: v0.6.0, a private GitHub repository installed as a Claude Code plugin. See "Pending".

## What is inside

| Skill | Load it before | Rules |
|---|---|---|
| `expo-rn-apps` | Expo/RN animation, reduced motion, EXPO_PUBLIC flags, Hermes perf, react-native-svg, Android text fit | 5 |
| `rn-render-perf` | dense or animated RN drawing (ownership, per-frame boundary traffic), Skia Canvas lifecycle, readiness deadlines, layer compositing, gfxinfo frame stats, an order of work | 5 |
| `android-builds-devices` | Gradle/prebuild, test APKs (arm64-only, fingerprint-gated incremental), adb and emulators, capture harnesses, shared hosts | 7 |
| `ui-motion-quality` | visual, layout or motion changes, pixel and contrast gates, recording timing, owner acceptance | 7 |
| `vercel-cost-cache` | Vercel deploys, headers, caching, static vs function, bill work | 5 |
| `data-persistence` | save or DB schema changes, Neon/Postgres URLs, timeouts, health checks | 5 |
| `testing-gates` | tests, detectors, benchmarks, A/B perf, quoted numbers | 7 |
| `store-release` | release AABs, test-ads proof, Play surfaces, store text | 6 |
| `agent-process` | delegation, waits and long commands, worktrees, merges, outward steps, speed changes | 6 |
| `tool-reliability` | file edits through the shell, zsh quoting and `find`, worktree-agent commands, repeated calls, timeouts, host-load claims, parked subagents | 7 |
| `code-and-doc-lookup` | code search, memory-note search, library API and version facts, pointing a note app or tool at memory, trusting an index, language server or docs service | 4 |
| `binary-and-wasm-porting` | untrusted-format parsers, caps and fuzzing, independent oracles and cross-checks, wasm32 builds, native-vs-wasm determinism, headless WebGPU tests | 5 |

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
python3 tools/lint-playbooks.py --no-claude     # same lint without calling `claude plugin details`
```

## Token budget (measured 2026-10-08, v0.6.0)

Skill descriptions load into every session, so they are the most expensive bytes.

| Measure | Skill listing (12 skills) | SKILL.md body, each |
|---|---|---|
| rendered listing lines `- agent-playbooks:<name>: <desc>`, chars / 2.8 (the lint) | 1,953 chars, ~698 projected (v0.5.0: 1,924 chars, ~688) | — |
| `claude --plugin-dir . plugin details agent-playbooks` | ~476 always-on (v0.5.0: ~469; R35 on the drift against v0.2.1's ~614) | ~960–1.5k on invoke |
| chars / 4 of the descriptions alone (old estimate, printed for comparison) | ~381 (v0.5.0: ~374) | 1,256–1,498 (v0.5.0: 1,077–1,499) |

The lint fails above 60 words per description, 700 projected tokens for the listing (estimate or `claude plugin details`, R20), or 1,500 tokens (chars/4) per body.

## Skill listing: why descriptions can vanish (2026-10-07)

Observed (controller session and this one, 2026-10-07): with well over 100 skills installed, most `agent-playbooks` skills were listed by name only; only `android-builds-devices` showed its description. Read from the installed CLI 2.1.269 (`@anthropic-ai/claude-code/bin/claude.exe`; the setting texts are its own schema descriptions):
- The listing has a character budget: `skillListingBudgetFraction` ("Fraction of the context window (in characters) reserved for the skill listing", default 0.01) × the model's context window × 4 chars per token, i.e. ~8,000 chars at 200k and ~40,000 at 1M. `SLASH_COMMAND_TOOL_CHAR_BUDGET` overrides it. Each entry's description (plus ` - <when_to_use>`) is capped at `skillListingMaxDescChars` (default 1,536; the docs state the 1,536 cap).
- Over budget, descriptions are dropped, not skills: every skill keeps its `- <plugin>:<name>` line. Descriptions are re-admitted greedily in order of a usage score (invocations, halving every 7 days, floor 10 %); never-used skills score 0 and keep listing order. A description that does not fit the remaining budget is skipped, so long descriptions lose first among equals.
- So skill count (total size), usage history and description length decide what is shown; plugin order only breaks ties among unused skills. A new plugin's unused skills are the first to go name-only, which is what was observed; `android-builds-devices` had been invoked before.
- A name-only skill can still be invoked by name, but an agent can only discover it from its name. Names here are descriptive, but trigger words in descriptions do nothing in a crowded session.
- Levers (owner's settings, not changed here): raise `skillListingBudgetFraction`, disable unused plugins, mark rarely needed skills `name-only` via `skillOverrides`, or run 1M-context models. `/context` shows the listing the model actually receives.

## How this avoids dumbing down future models

- **Kinds.** Invariants (safety, irreversibility, owner preferences, quality gates) state why and do not expire. Facts state the versions and conditions they were measured under and expire with them. Heuristics, the only "how to" rules, state the goal they serve, allow an override with stronger evidence, and expire within 90 days unless re-validated.
- **Gates over procedures.** Rules say what must be true at the end, so a smarter model can reach it its own way. Procedures remain only where the procedure is the invariant (the release recipe).
- **Staleness is visible.** The lint warns on old facts and expired heuristics; `check-applicability.py` marks rules measured on other versions as unverified here.
- **Retirement is recorded.** `retired/` keeps the reason and the reopening condition, and the lint refuses a retired id.
- **Measured, then corrected.** The eval harness in [evals/](evals/README.md) runs fixed tasks with and without the plugin on the current and any new model. Rules that do not raise the gate-pass rate, that cost tokens without benefit, or that make a newer model worse are trimmed or retired.

This cannot be proven in advance. Whether a rule helps or hinders a future model is an empirical question that only the eval harness, run with replicated runs, can answer. Until it has run, every claim of benefit in this repo is a hypothesis.

## Pending

- The first eval run (designed and stubbed; never run). 16 cases; ev11 and ev12 were added in v0.2.0, ev13 and ev14 in v0.3.0, ev15 and ev16 in v0.5.0.
- The `fg-wait-guard` hook ([tools/hooks](tools/hooks/README.md)) is an approved experiment, registered by the owner 2026-10-07 11:45; it is not a rule.
- TOOL-008 is re-measured with a harness-audit run on 2026-11-06 (its expiry forces the look), from transcripts: the hook logs decisions, not outcomes.
- The `fg-wait-guard` judgement: `harness-audit --judge-fg-wait` on 2026-11-06 against the frozen baseline.
- ANDR-002's time saving is unproven on a loaded host; the bytes carry the rule.
- The lint projects ~698 always-on tokens (1,953 of the 1,960 chars the budget allows) and Claude Code ~476; the budget is 700 projected (R20). 7 chars of headroom: the next trigger or skill needs a trim or an owner decision on the budget (R47, R58). In crowded sessions descriptions may still be hidden (see "Skill listing").
- PORT-003's deep-reach floor and re-introduced-defect check are INFERRED until LOMN M1a-4 Task 1 records its fuzz results (R30).

## Candidates not trialled

- **Hindsight** (`vectorize-io/hindsight`, memory for agents): NOT TRIALLED, owner decision; not retired. Ingestion needs an LLM extraction pass over every note. No local model is installed, and the cloud path would send about 0.7 M tokens of notes (536 notes, ~2.7 MB, including ad-network keys) to a provider. Its Claude Code plugin hooks `UserPromptSubmit` (every prompt) and `Stop` (every turn). It cannot be judged against LOOK-001 until the owner approves a provider and a spend cap, or a local model with free disk; first check whether facts derived from a deleted or corrected note disappear from recall. Source: arrows-game `docs/process/obsidian-memory-trial-2026-10-08.md` §6.
- **Obsidian Local REST API plus an MCP bridge:** NOT TRIALLED. It needs Obsidian 1.13.1 or newer (1.1.9 installed), a GUI plugin enable and a running app, and offers no retrieval that MCPVault (LOOK-904) lacks.
- **Owner browsing:** Obsidian opened on a one-way read-only copy of the notes left all 492 of 492 byte-identical (LOOK-003). The refresh script is in the trial doc §7; it is not part of this plugin.
