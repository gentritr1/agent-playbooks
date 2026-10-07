---
name: testing-gates
description: Use before writing or trusting a test, gate, detector or benchmark, comparing A/B performance runs, quoting a percentile, count or threshold, or reviewing a claim that something is fixed.
---

# Testing gates

A gate that cannot fail proves nothing. Each rule below says what must be true before a verdict counts.

### TEST-001 · New tests go red first and have teeth
- **Rule:** Show each new test failing on the pre-fix tree, and a mutant of the guarded line failing it.
- **Kind:** invariant — why: tests that pass on the broken tree, or catch no mutant, approve anything.
- **Evidence:** arrows-game 2026-09-24: per-guard mutation table, every mutant caught; secret-dictator-v2: all seven mutants first "reported clean"; geoguesser: a 20-line test killed all ten "unreachable" mutants → [teeth](evidence/teeth.md)
- **Confidence:** VERIFIED
- **Gate:** the report lists the red run, each mutant with `caught > 0`, and a byte-identical restore
- **Valid while:** any test runner · last_validated: 2026-10-06
- **Source:** TEST-001

### TEST-002 · A zero or a pass needs a positive control and primary data
- **Rule:** Fire every detector on a known-true case in the same build, and recompute gates from primary data.
- **Kind:** invariant — why: a blind instrument reads zero and a self-reported flag reads pass.
- **Evidence:** arrows-game 2026-09-19: "0/10 survive" grepped a dev-only log in a release build; geoguesser 2026-09-16: a gate trusted a `reconciled` flag and passed n=240 against 18,432 → [teeth](evidence/teeth.md)
- **Confidence:** VERIFIED
- **Gate:** each zero count is printed beside its positive-control count (> 0); the gate reads raw rows, not report flags
- **Valid while:** any detector · last_validated: 2026-10-04
- **Source:** TEST-002

### TEST-003 · A performance shift beats the null and replicates
- **Rule:** Claim a shift only when the median difference exceeds a same-build null spread and replicates across interleaved runs, or passes a permutation test.
- **Kind:** invariant — why: one-shot orderings are coin tosses and a range-inside-range test fails identical builds.
- **Evidence:** arrows-game 2026-09-25: range-inside-range failed identical builds on 4 of 5 metrics (n=8); 2026-09-30: +2.4034 ms against a 0.0781 ms null, replicated in 16 shuffled runs → [perf-stats](evidence/perf-stats.md)
- **Confidence:** VERIFIED
- **Gate:** the report shows n per arm, run order, null spread, effect and p or the replication; no claim below the null spread
- **Valid while:** emulator or device timing · last_validated: 2026-10-07
- **Source:** TEST-003

### TEST-004 · Reconcile sample counts before quoting a percentile
- **Rule:** Print counted samples against window × expected rate beside every percentile.
- **Kind:** invariant — why: partial or overflowing samplers give plausible percentiles of the wrong data.
- **Evidence:** merge-kit: 1229 of ~1800 frames, then 0, then 1; arrows-game 2026-09-30: a parser rejected every gfxinfo row (trailing comma) → [perf-stats](evidence/perf-stats.md)
- **Confidence:** VERIFIED
- **Gate:** expected vs counted samples printed per window; read the windowed instrument before slow dumps
- **Valid while:** any sampler · last_validated: 2026-10-06
- **Source:** TEST-004

### TEST-005 · Measure the configuration users get, and watch the control arm
- **Rule:** Assert the build's flags from runtime logs, and compare the control arm with the previous round before reading the treatment.
- **Kind:** invariant — why: a benchmark of the wrong configuration or a drifting control creates confident false causality.
- **Evidence:** arrows-game 2026-09-30: a benchmark missed a camera flag and measured a 10 dp tier players never see (~29 dp); 2026-10-02: the OFF control ran 6× slower than last round → [perf-stats](evidence/perf-stats.md)
- **Confidence:** VERIFIED
- **Gate:** flags and APK sha are recorded and matched by a runtime log line; host load is logged per arm
- **Valid while:** shared dev host · last_validated: 2026-10-07
- **Source:** TEST-005

### TEST-006 · Numbers from briefs are hypotheses until recounted
- **Rule:** Recount any target, share, baseline or test count from live code or data at the current commit before using it.
- **Kind:** invariant — why: quoted numbers go stale and unmeasured thresholds are often unreachable.
- **Evidence:** arrows-game 2026-10-06: a brief's "1/2 Normal" share was 4/6 in code; lucky-shelf: brief thresholds caught 84 % of days → [stale-numbers](evidence/stale-numbers.md)
- **Confidence:** VERIFIED
- **Gate:** every number in the report names the command and commit that produced it
- **Valid while:** any project · last_validated: 2026-10-06
- **Source:** TEST-006

### TEST-007 · Jest via Babel does not type-check
- **Rule:** Run `tsc --noEmit` over new and changed test files.
- **Kind:** fact — jest-expo transforms with Babel, so type errors in tests pass jest.
- **Evidence:** arrows-game 2026-10-06: tier-label tests passed jest while `tsc --noEmit` failed on them → [stale-numbers](evidence/stale-numbers.md)
- **Confidence:** VERIFIED
- **Gate:** `npx tsc --noEmit` exits 0 with the changed tests inside its `include`
- **Valid while:** `jest-expo@57` · last_validated: 2026-10-06
- **Source:** TEST-007

## Gates before you report done
Red then green, with a caught mutant (001); positive control beside each zero (002); null spread and replication for perf (003); sample reconciliation (004); flags from runtime (005); provenance of every number (006).

## Not covered / defer to
TDD workflow: `superpowers:test-driven-development`. Final claims: `superpowers:verification-before-completion`. Debugging: `superpowers:systematic-debugging`.
