# Contributing a rule

## The rule format (every rule, no exceptions)

```markdown
### TEST-003 · A performance shift beats the null and replicates
- **Rule:** one terse do or don't.
- **Kind:** invariant — why: <reason it never expires>
        | fact — <the measured truth>
        | heuristic — goal: <what it serves>; override: stronger case evidence, stated in the report; expires: YYYY-MM-DD
- **Evidence:** project, date, numbers → [name](evidence/<file>.md)
- **Confidence:** VERIFIED | INFERRED — <why it is unmeasured>
- **Gate:** the exact check that proves the rule was followed
- **Valid while:** `pkg@version` `ctx:<context>` tokens, platform, conditions · last_validated: YYYY-MM-DD
- **Source:** TEST-003
```

- **Ids** are `PREFIX-NNN`, stable, unique across skills, never reused. Retired ids live in `retired/`.
- **Kinds.** *Invariant*: safety, irreversibility, owner preference or quality gate; never expires, states why. *Fact*: a measured truth about tools or environment; expires when its versions or conditions change. *Heuristic*: how to do something; states its goal, allows an override with stronger evidence that the agent states in its report, and expires within 90 days of `last_validated`.
- **Confidence.** VERIFIED means measured, replicated or gate-proven in a named run. INFERRED means plausible and unmeasured; say why.
- **Valid while.** Backticked `name@version` tokens are compared with the target project by `tools/check-applicability.py` (installed version first, then the declared range). `ctx:` tokens (`android`, `vercel`, `neon`, `postgres`, `web`, `ads`, `react-native`, `expo`, `jest`, `git`, `ios`, `any`) are detected from the project. `claude-code@<version>` tags rules about harness behaviour (timeouts, the worktree guard, the Bash default); it is compared with `claude --version` and is UNKNOWN when the CLI cannot be read. Free text records platform and conditions.
- **Evidence files** are short extracts, each with a `**Source:**` line naming project paths. No raw transcripts, no secrets, no ad unit ids, no hostnames, no personal data beyond project names.
- **Prefer goals and gates to procedures.** Write what must be true at the end. Keep a procedure only when the procedure is itself the invariant (the release recipe).

## Budgets (the lint fails above them)

- `description`: triggers only, ≤ 60 words. The always-on skill listing (each skill rendered as `- agent-playbooks:<name>: <description>`) ≤ 700 projected tokens: rendered chars / 2.8, and the `claude plugin details` always-on number when `claude` is on PATH (CHANGELOG R20). Put the trigger words first; see "Skill listing" in the README for why descriptions can vanish in crowded sessions.
- `SKILL.md` body ≤ 1,500 tokens (chars / 4). Detail goes to `evidence/`, reached by links. A skill never tells an agent to read all its evidence.
- 5–7 rules per skill fit the budget; the lint warns above 15.

## Promotion path: project lesson → playbook

1. A lesson is recorded in its project (`docs/engineering-lessons.md`, a report, or project memory) with observation, cause or hypothesis, correction and verification status.
2. It is a candidate when it transfers: it would change what an agent does on a different project.
3. It enters as a rule when it has a measured number or a gate that ran, an evidence extract, and a `Valid while` that names the versions and conditions.
4. Duplicates merge into one rule; the evidence file keeps every source.
5. A second firing in another project raises it from INFERRED to VERIFIED or widens its `Valid while`.

## Review gate (before a rule merges)

- `python3 tools/lint-playbooks.py` passes and `python3 -m unittest discover -s tests` passes.
- The reviewer opens each cited source and confirms each quoted number. A quote that cannot be found is removed, not paraphrased.
- The gate is runnable or observable by a third party.
- Contradicting evidence is cited and resolved by the newer, better-controlled run.
- A heuristic names its goal, override clause and expiry; an invariant names why.
- If the rule changes agent behaviour, an eval case covers it or the CHANGELOG says why not.

## Contradictions resolved in v0.1

| Topic | Sources | Resolution |
|---|---|---|
| Can a Hermes bundle be grepped? | block-blaster: "find nothing regardless"; geoguesser-app: `strings \| grep -c` gave false zeros, raw bytes worked; arrows-game: UTF-8 and UTF-16LE counts with a positive control | Newer, positive-controlled evidence wins: count raw bytes in both encodings after a control string is found (EXPO-002, STORE-001). |
| Proof of test ads | geoguesser-app same day: verbose ad logcat called reliable, then said to no longer show unit ids | The bundle proof is the gate (STORE-001); logcat test-device lines are supporting evidence only. |
| Disk threshold before builds | arrows-game 5 GB (2026-09-16), raised to ~7 GB after cold caches vanished (2026-09-28/29); geoguesser-app 2.5 GiB for a device session | 7 GB for a cold native build (ANDR-004); smaller steps keep their project thresholds. |
| `android/` committed vs generated | geoguesser-app commits it and never prebuilds; block-blaster and arrows-game generate it | Project convention, not a rule; STORE-002's gate says "clean build (`prebuild --clean` where `android/` is generated)". |
| Which model or tool implements | manga-reader, blink-heist, futurisma-race, geoguesser-app and planet-drop disagree | Owner preferences without a controlled measurement: excluded until the eval harness compares them. |

## Contradictions resolved in v0.2

| Topic | Sources | Resolution |
|---|---|---|
| One simple command per call | v0.1.1 TOOL-003 (study draft: compound OR 2.07); §11 (a chained call does several units of work: [inferred]) | §11 wins: only the worktree-guard fact stays (TOOL-007); TOOL-003 retired. |
| Stop after 2 identical failures | study draft (INFERRED threshold); §11 (21 of 41 loops succeeded in the end) | §11 wins: "state what changed" (TOOL-008); TOOL-004 retired. |
| Is arm64-only faster? | speed audit archive 3.5 vs 7.7 min (confounded); E1 interleaved −237 s inside a 429 s null spread | The controlled run wins: time unproven; the rule rests on byte identity (ANDR-002). |
| Monitor/background odds ratios as evidence | v0.1.1 PROC-001 cited 0.06 and 0.03; §11 review | Definitional (a detached call cannot hit the cap); PROC-001 cites cap hits and hours instead. |
| `find` on `-`-named directories "fails silently (exit 0)" | §11; standalone re-run 2026-10-07 exits 1 with `bfs: error` | Both hold: silent in a pipeline (exit 0, no output), loud alone. TOOL-002 says so. |
| Where library facts come from | AGENTS.md "read the versioned docs"; 2026-10-07 trial (versioned docs drift to the newest patch) | Installed package first, then the versioned URL (LOOK-002). |

## Procedures converted to goal + gate in v0.1

Ten source procedures were rewritten as a goal plus gate: EXPO-001 (scale, relaunch, restore steps → static state visible in a capture), EXPO-002 (stop daemon, clear cache, grep → byte counts with control), ANDR-003 (fingerprint and Gradle commands → byte-identical artifact), ANDR-005 (pin Node, check files, compare sha → own exit code and new sha), ANDR-006 (delete dump, wait, check activity → proven screen before input), UI-005 (ffprobe steps → ≥ 90 % frame density), TEST-001 (mutate, run, restore, cmp → listed red run and caught mutants), PROC-001 (loop template → wait matches failure), PROC-005 (create the worktree yourself → HEAD equals the stated SHA), VERC-003 (run `vercel build` → know what publishes). Kept as procedures on purpose: STORE-002 (the release recipe is the invariant) and PROC-006 (one state change per step).

## What was excluded, and why (examples)

| Excluded | Why |
|---|---|
| The Arrows product module's file layout, skin contract K1–K8 values (rim .48, 29.387754 dp), level indices, generator fingerprints, the DotNetRandom port defect | Arrows-specific; they stay in that repo's docs |
| Emulator serials, AVD names, tap coordinates, the owner's ad unit ids and SDK keys | Host- or account-specific, and identifiers that must not travel |
| Game-design findings, reward path, seasonal plans, sound choices | Owner product decisions, not engineering practice |
| Reanimated dead-tag internals (PERF-DEADTAG) | Version-specific mechanism with a project-specific fix; only the disproven generic fix is kept, in `retired/` |
| Codex vs Opus vs Sonnet role splits | Conflicting owner preferences with no controlled measurement |
| A report script that rewrote its own status line from "pending" to "pass" (BOOK-01) | One observation; the claim it changed was backed by a device file, so no measured failure |
| Hidden browser-pane rendering (≥ 10 projects), Node v14 nvm default (~9 projects), `color-mix(in oklch)` hue shift, Tailwind classes that compile to nothing | Cross-project and replicated, but not re-verified in this pass and outside the body budgets; candidates for v0.2 |
| Godot and Unity headless gotchas | No playbook covers those engines yet |
