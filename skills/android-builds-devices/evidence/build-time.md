# Build time and stale artifacts

**Source:** arrows-game `docs/process/speed-audit-2026-10-07.md` §(a) Builds, E1, E2 and "Surprises" (222 Gradle logs, 2026-09-16..10-07); arrows-game `docs/process/speed-experiments-2026-10-07.md` (E1/E3 decision rules, pre-registered, no result yet); arrows-game memory `shared-host-contention.md` (Node drift, 2026-09-29); block-blaster memory `local-android-build-traps.md` (2026-07-18); geoguesser-app memory `dont-pipe-long-builds-through-tail.md` (2026-08-28).

## Gradle runs (arrows-game, measured)
| Build class | n | Total | Median | p90 |
|---|---|---|---|---|
| Incremental (< 400 tasks), success | 175 | ~5.0 h | 1.1 min | 3.4 min |
| Clean test APKs (≥ 400 tasks) | 31 | 3.56 h | 4.5 min | 8–12 min (max 35.4 under load) |
| Clean release AABs | 6 | 1.03 h | 10.7 min | 14.6 min |

| ABIs | Clean median |
|---|---|
| arm64-v8a only | 3.5 min (n=17) |
| arm64-v8a + x86_64 | 7.7 min (n=7) |
| armeabi-v7a + arm64-v8a (release) | 10.7 min (n=6) |

The audit notes the ABI comparison is confounded by date and host load. Both AVDs have `abi.type=arm64-v8a`. `prebuild` itself takes 5–18 s; the cost of `--clean` is the ~618 of 646 Gradle tasks it forces, against ~27 incremental. E1 (fingerprint-gated incremental build, byte-identity guard) is pre-registered and unrun, which is why ANDR-003 is INFERRED.

## Stale artifacts
- block-blaster: `./gradlew … | tail -5` reported the pipe's exit code, so BUILD FAILED surfaced as exit 0 and a 2-hour-stale APK was installed and re-tested as if it were the fix.
- geoguesser-app: the same pipe hid a successful build; a redundant second build was started on top of it.
- arrows-game 2026-09-29: the shell resolved `node` to v14; `expo prebuild` warned but exited 0, Gradle failed, and the script copied the previous AAB under the new version name (same sha256). Rules adopted: pin Node, check `android/app/build.gradle` exists after prebuild, exit on Gradle failure before copying, compare the output sha with the previous build.
