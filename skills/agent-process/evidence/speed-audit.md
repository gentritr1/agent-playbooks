# Where helper time went (arrows-game, 2026-09-16..10-07)

**Source:** arrows-game `docs/process/speed-audit-2026-10-07.md` (93 helper transcripts, 12,263 tool calls, scripts in `scripts/process/`); `~/.claude/CLAUDE.md` §10; arrows-game `docs/process/speed-experiments-2026-10-07.md` (E2 pre-registration).

| Category | Hours | Share of 101.3 active h |
|---|---|---|
| Model (thinking, output, API) | 34.6 | 34.2 % |
| Perf/gate series waits | 23.5 | 23.2 % |
| Analysis/driver scripts | 9.6 | 9.5 % |
| Other waits | 7.8 | 7.7 % |
| Jest | 7.1 | 7.0 % |
| Builds | 6.3 | 6.2 % |
| Device capture and adb | 5.5 | 5.4 % |
| APK install | 2.9 | 2.9 % |

- Calendar: in 485.5 h, something ran for 94.9 h; 390.6 h (80 %) had nothing running. Helpers ran one at a time for 67.1 h, two for 16.2 h.
- Model time tracks output tokens (~11 s per 1k), not context size.
- Premises that did not hold: lessons-file reads were small (15 of 92 agents, ~93k tokens); literal retries cost 0.74 h.
- Jest: the same full suite took 55–70 s quiet and 219 s loaded (max 777 s).
- Route experiments are pre-registered before data is opened (E2-R1, 2026-10-07T00:17Z) and judged against a null spread. Results (phase 2, 2026-10-07): E3 fingerprint-gated test builds adopted (598 → 88 s, byte-identical; ANDR-003); E1 arm64-only adopted on bytes, time unproven (ANDR-002); E2 early stop rejected, 15 of 87 verdicts flipped (TEST-902); E4 load gate adopted as tooling.
