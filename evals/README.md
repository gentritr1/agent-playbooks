# Model-upgrade evals

Designed and stubbed; not run yet. The question each run answers: on this model, do agents pass more gates with the playbooks loaded than without, at what token cost, and does any rule make a newer model worse?

## Cases

Sixteen small, fixed tasks drawn from real past failures. Each scaffolds its own workspace (`setup.sh`) and is graded by `claude plugin eval` graders: `regex` on files, the trace or the final message, `tool_used`, and `llm` rubrics with explicit PASS/FAIL conditions. Graders check outcomes where the runner can see them (a file the scaffold writes, a harness marker in the trace) rather than the method used; `claude plugin eval` has no duration or custom-code grader (docs: code.claude.com/docs/en/plugin-evals), so "no foreground call past 120 s" is the absence of the 2-min cap marker plus no foreground `timeout` above 120000, the only two ways past it.

| Case | Real origin | Rules | Graders (pass when) |
|---|---|---|---|
| ev01-test-ads-proof | ADMOB-B, PETAL-ADS-01 | STORE-001, EXPO-002 | final message names the production unit hidden in UTF-16LE; says do not install; rubric: positive control reported |
| ev02-cache-headers | morse-code-trainer, snaxx-tech | VERC-001, VERC-002 | `vercel.json` has a 1-year immutable rule and `max-age=0, must-revalidate`; dead `/static/` pattern gone; rubric: every asset class covered |
| ev03-fix-test-no-weaken | Workflow Studio 528.0000000000001 | TEST-001 | original assertion byte-identical; `node --test` was run; rubric: red, green and a mutant reported |
| ev04-perf-gate-null | W4-07 range-inside-range, ART-SKINS-01 | TEST-003 | verdict is no demonstrable regression; rubric: compares against the same-build null, states n, rejects range containment |
| ev05-reduced-motion | shipping defect 2026-09-09, REWARD-01 | EXPO-001, UI-002 | file sets a reduce-motion policy; rubric: static highlight survives; device check reported UNVERIFIED |
| ev06-background-wait | global harness §9, orphaned `pgrep -f` loops | PROC-001 | outcome: no foreground call observed past 120 s (no cap marker in the trace, no foreground `timeout` above 120000); the build ran exactly once (`.runs`); no `pgrep -f`; failure reported |
| ev07-stale-brief-number | W3-20 tier shares | TEST-006 | `SHARES.md` uses 4/6 from code; rubric: brief flagged as stale with the file cited |
| ev08-pixel-null-control | ART07 316-px failure, ART08 null | UI-003 | verdict pass/unchanged; rubric: base-vs-base null measured first, pixel counts given |
| ev09-save-schema-change | planet-drop wipe, geoguesser profile wipe | DATA-001 | test loads `fixtures/v3-save.json`; rubric: old save keeps level 42 through `load()` |
| ev10-stale-build-artifact | block-blaster tail pipe, arrows-game copied AAB | ANDR-005 | `install.sh` never called; failure reported |
| ev11-long-command-timeout | §11: 218 of 257 cap hits ran to the 10-min cap at a self-raised timeout | PROC-001, TOOL-009 | outcome: no foreground call observed past 120 s (as ev06); the script ran exactly once; the total is reported |
| ev12-installed-library-facts | 2026-10-07 tool trial: Context7 and the docs answered for another Reanimated version | LOOK-002 | answer says 0.10; rubric: installed 4.5.1 and its package file cited, 0.11.x not allowed |
| ev13-oracle-shared-constant | LOMN M1a-3: FourCC sort ids byte-swapped in implementation and oracle, 9/123 areas | PORT-001 | answer refuses sign-off and names the byte order; rubric: constants checked against data or spec, not against the oracle |
| ev14-parser-cap-from-maxima | LOMN M1a-3: a 64 MiB table reached 1,273 MB on wasm32; real max 15 records | PORT-002 | final message states 15; `table.py` has a cap constant; rubric: cap ≥ 16× the measured max, no per-record copy, samples parse, no partial state |
| ev15-monitor-by-design | gold-pdf-bot incident 1 (2026-10-08): a refused database login lost data for ~3 h, every reason swallowed | DATA-006, DATA-003 | PLAN.md names a drill; rubric: alive signal, reason kept outside the failed database, where and how fast, computed free-tier cost, drill (or asks the owner) |
| ev16-env-change-is-a-deploy | gold-pdf-bot incident 1: password edited without a redeploy, then Neon's `sslmode=require` copy format | VERC-006 | final message says redeploy; rubric: redeploy, fix sslmode for `db.py`, test the exact value first and confirm the next stored request |

`python3 evals/run-evals.py cases` prints the same list from the case files.

## Protocol

1. Lint and self-tests pass on the commit under test.
2. In a throwaway worktree of this repo, run `claude plugin eval` twice per model: the current model and, when one ships, the candidate. The first run uses `--ablation with-without`, which gives every case a no-plugin arm; the second uses `--ablation none` and is a second, independent with-plugin arm (`with2`), the with-vs-with null. `--runs 3` (minimum) gives replicated runs; each run gets a fresh scaffold. `python3 evals/run-evals.py plan --current <id> --candidate <id>` prints the exact commands.
3. Record per run: gate pass (case score), tokens, tool calls, tool errors, wall-clock, owner-visible defects (from the owner's review of any output that ships). Put them in `METRICS.csv` (columns in `run-evals.py`).
4. `python3 evals/run-evals.py decide METRICS.csv` applies the decision rule. Record the verdicts in `CHANGELOG.md`; move retired rules to `retired/` with the numbers.

## Decision rule (§6 noise rules)

- Runs are paired by repetition. **IMPROVES:** the plugin arm wins at least 2 pairs and loses none. **WORSENS:** it loses at least 2 and wins none. Anything else, including a single win, is NO-EFFECT. Fewer than 3 runs per arm decides nothing.
- **With-vs-with null.** The effect (mean pass with − without) must exceed the null spread |mean pass with − with2|, where `with2` is an independent repeat of the with-plugin arm. An IMPROVES or WORSENS inside that spread is NO-EFFECT ("within null"): two runs of the same arm already differ that much. A case without 3 `with2` runs is INSUFFICIENT.
- Current model: IMPROVES → keep; WORSENS → retire; NO-EFFECT → trim when the plugin arm uses > 10 % more tokens, else keep but watch.
- Candidate model: a rule whose case WORSENS on the newer model is removed.
- Any increase in owner-visible defects with the plugin retires the rules the case covers.
- A verdict that matters is re-run once before acting on it; a one-run flip is noise.

## Cost estimate per run (INFERRED; the first run measures it)

- 14 cases × 3 arms (with, without, with2) × 3 runs = **126 agent runs per model**, plus LLM-judge calls (default judge: haiku, 3 votes per `llm` grader).
- Each case is capped at 12–20 turns and 300–600 s. Expect roughly 0.2–0.8 M input tokens (mostly cache reads) and 3–8 k output tokens per run, so about 25–101 M input and 0.4–1.0 M output tokens per model (126 runs × the per-run range).
- Wall-clock: about 2.7–5.3 h per model serially (v0.2 estimate scaled by 14/12); `-j 2` to `-j 4` shortens it but shares one rate limit.
- `--max-cost-usd` in the printed command is a hard ceiling; set it from the first run's measured cost.

## When to run

- A new model id becomes available or becomes the default.
- Every 90 days (the heuristic expiry window).
- A large playbook change: a new skill, more than 5 rules changed, or a description rewrite.

## Known limits

- `claude plugin eval` result files (`aggregate-result.json`) have not been seen yet; the conversion to `METRICS.csv` is written after the first run.
- Scaffolds were executed locally and produce the intended traps (UTF-16-only production id, failing float test, failing build next to an old APK, a null arm as wide as the treatment; ev11's script runs ~200 s and prints its total, ev12's package files parse; ev13's oracle prints 3/3 equal while no record matches either priority id; ev14's 18 samples peak at 15 records and a 4 MB crafted table took ~386 MB RSS in the unhardened parser). The graders themselves have not run; ev11's timeout regex was checked against 12 sample tool inputs with Node's regex engine, assuming the grader matches the JSON-serialised input as ev06's does.
- Case scores measure these twelve traps, not the whole playbook. A rule with no case is untested by this harness; the CHANGELOG lists such gaps when they matter.
