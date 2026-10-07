# Changelog

## 0.1.0 · 2026-10-07 (local, unpublished)

First version: 8 skills, 50 rules (47 VERIFIED, 3 INFERRED; 32 invariants, 12 facts, 6 heuristics), 24 evidence files, 8 retired ideas, lint and applicability tools with self-tests, and a designed but unrun eval harness (10 cases).

Sources: the global harness (`~/.claude/CLAUDE.md` §1–§10), arrows-game `docs/engineering-lessons.md`, `docs/process/speed-audit-2026-10-07.md`, `docs/process/graphify-trial-2026-10-07.md`, `docs/performance/field-guide.md`, `docs/skins/README.md`, `docs/next-level/reports/*`, and project memory of arrows-game, geoguesser-app and sibling projects (block-blaster, lucky-shelf, merge-kit, planet-drop, secret-dictator(-v2), tondo, form-studio, morse-code-trainer, snaxx-tech, wordle, apollonia-events, gold-pdf-bot, manga-reader, futurisma-race, offbeat). Quotes from sibling memory were spot-checked against the files before use.

### Rulings (judgement calls made without the owner; reverse any of them by editing this list)

- **R1 · `neon-postgres` became `data-persistence`.** Our Neon evidence is real but small (wake time, timeouts, pooler, outages), and the strongest replicated data lesson is the save-wipe scar from client persistence. One skill covers both. The new name also avoids colliding with the owner's existing `neon-postgres` skill, which it defers to.
- **R2 · Kinds and staleness.** Invariants are exempt from the 90-day staleness warning (they never expire) but still need a valid `last_validated`. Facts and heuristics warn after 90 days; an expired heuristic warns in the lint and is labelled EXPIRED by `check-applicability.py` rather than failing the build, so the repo does not break on a calendar date.
- **R3 · Token estimate.** Budgets use chars/4, as specified. `claude plugin details` projects ~546 always-on tokens (under 600) and 1.7k–2.3k per body on invoke, about 1.5× the chars/4 figure. Meeting 1,500 on Claude Code's projection would mean ~4 rules per skill; left for the owner to decide.
- **R4 · Gate checklist.** Each SKILL.md keeps a one-line gates checklist that points at rule ids instead of repeating the gate text, to stay inside the body budget.
- **R5 · Applicability statuses.** Exactly the three asked for. A rule whose `ctx:` context is absent from the project is UNKNOWN with the reason "ctx not detected"; a rule with no version or context tokens is version-free and APPLIES.
- **R6 · Manifest owner.** `marketplace.json` names "agent-playbooks maintainers" and `plugin.json` has no author: no personal data until the owner confirms the name. `claude plugin validate` passes with one warning (no author); `--strict` fails on that warning only.
- **R7 · Eval harness on `claude plugin eval`.** The installed CLI ships an eval runner with case files, graders and a with/without-plugin ablation arm, so the cases use its `case.yaml` format instead of a custom runner. `evals/run-evals.py` prints the commands and holds the decision rule; it never starts a model session.
- **R8 · Skill-writing TDD.** `superpowers:writing-skills` asks for pressure tests with subagents before each skill. That role is assigned to the eval harness (with/without arms, replicated), which the owner asked to be designed but not run; no baseline was run in v0.1.
- **R9 · Pending section stays a stub.** `~/.claude/process-metrics/reports/` does not exist yet and no tool-reliability study was found anywhere, so the `agent-process` section names where its data will come from and holds no rules.
