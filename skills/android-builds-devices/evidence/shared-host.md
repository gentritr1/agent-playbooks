# Shared host: device collisions and disk

**Source:** arrows-game memory `shared-host-contention.md` (2026-09-16..10-01), `codex-delegation-setup.md` (2026-09-19); arrows-game `docs/engineering-lessons.md` ("Android capture tooling: bound commands and preserve raw evidence", 2026-09-30); geoguesser-app memory `disk-nearly-full-gates-fail-enospc.md` (2026-10-05), `avd-dies-under-host-memory-pressure.md` (2026-10-02/07/08); geoguesser-app `docs/engineering-lessons.md` L6 and `docs/plan/evidence/device-2026-10-07/bakeoff/install*.log`, `scripts/bakeoff-when-quiet.sh` (2026-10-08); futurisma-race memory `consolidation-2026-10-04.md`.

## Device collisions
- arrows-game 2026-09-26 (W2-09): parallel subagents of one controller both drove the same emulator; each killed the other's app and one ran on the other's APK.
- arrows-game 2026-09-19: a delegate ran a bare `adb reconnect` that bounced another session's emulator; the shared brief now forbids any adb call without `-s`.
- arrows-game 2026-09-30 (ART-SKINS-01): a capture/perf batch was discarded after another host process issued adb screenshot commands to the same emulator.
- geoguesser-app: the AVD died under host memory pressure; "any foreign Gradle build during a run is enough" (observed 3 times).
- Detection used in arrows-game: watch `logcat` for `Start proc`/`Force stopping` lines for the app that the task did not issue.
- geoguesser-app 2026-10-08 (observation, not yet a rule): on an 8-core host, 4 `adb install`s of a 33–45 MB QA APK took the API 36 AVD's system_server down at host load 25–45 (install-time dexopt starved the network stack into a background ANR, then "Lost network stack"); installs worked at load ~11 the same night, and the bake-off APK that had failed twice with `Broken pipe` installed after the 1-minute load stayed below 18 for three samples 20 s apart (`bakeoff-when-quiet.sh`). A load gate before emulator installs is a candidate for ANDR-004; the failing level was not swept, and the lessons file's "< 15 for 2 min" is a judgement between the two observations.
- geoguesser-app 2026-10-08 (`docs/engineering-lessons.md` L6): on a starved AVD a system "System UI isn't responding" dialog appears over the app. The harness taps Wait and logs it, so the run's log shows the starvation; an ANR of the app under test is never dismissed, because that is a finding, not noise.

## Disk
| Project, date | Observation |
|---|---|
| arrows-game 2026-09-16 | free disk fell 11 GB → 1.8 GB in ~2 h while this session built one APK/AAB; another session was running |
| arrows-game 2026-09-28/29 | `~/.gradle/caches` vanished twice; a cold release build re-downloads ~2.8 GB and writes ~4 GB under `node_modules/*/android`; budget ~7 GB, not 5 |
| arrows-game 2026-09-27 | disk fell 3.9 → 0.18 GB in minutes while another session ran |
| geoguesser-app 2026-10-05 | 464 MiB free; the check script failed with ENOSPC; re-run passed after freeing space; device rule stops below 2.5 GiB |
| futurisma-race 2026-10-04 | 629 MB free; an `isolation: worktree` checkout died mid-checkout |

A `df` taken at task start is stale by the time the build starts; measure right before the step.
