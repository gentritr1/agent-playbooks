# Build time and stale artifacts

**Source:** arrows-game `docs/process/speed-audit-2026-10-07.md` §(a) Builds, E1, E2 and "Surprises" (222 Gradle logs, 2026-09-16..10-07); arrows-game `docs/process/speed-experiments-2026-10-07.md` (phase 2: E1 arm64-only and E3 fingerprint-gated builds, pre-registered rules, measured 2026-10-07); arrows-game commit `ca0b0f5` (owner approves E3 and E1, 2026-10-07); arrows-game memory `shared-host-contention.md` (Node drift, 2026-09-29); block-blaster memory `local-android-build-traps.md` (2026-07-18); geoguesser-app memory `dont-pipe-long-builds-through-tail.md` (2026-08-28).

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

The audit notes the ABI comparison is confounded by date and host load. Both AVDs have `abi.type=arm64-v8a`. `prebuild` itself takes 5–18 s; the cost of `--clean` is the ~618 of 646 Gradle tasks it forces, against ~27 incremental.

## Phase-2 experiments (arrows-game 2026-10-07, measured)
Numbering is the phase-2 brief's: E1 = arm64-only, E3 = fingerprint-gated incremental. One interleaved series A1 B1 D1 A2 B2 D2 A3 B3 D3, one build at a time, host load 12–61 throughout (other sessions' emulator, jest and Gradle). A = clean `arm64-v8a,x86_64`; B = clean `arm64-v8a`; D = fingerprint-gated `arm64-v8a`. Time = the build script's wall time. Decision rules were written before any build finished: a saving counts only if the median shift exceeds the larger within-arm range and every pair agrees with disjoint ranges.

| | A (2 ABIs) | B (arm64, clean) | D (gated, incremental 3/3) |
|---|---|---|---|
| Total s | 909, 835, 480 (median 835) | 660, 598, 527 (median 598) | 92, 70, 88 (median 88) |
| Gradle tasks executed | 618 | 606 | 25 |

- **E3 (ANDR-003): adopt.** B → D −510 s (6.8×); null spread 133 s; every pair faster (+568, +527, +439 s); ranges disjoint. D1 = B1, D2 = B2, D3 = B3 as whole APK files (sha256). Controls: a comment appended to a Kotlin file in a native module turned the decision `clean`, and reverting restored `incremental`; a TypeScript probe left the fingerprint unchanged, the incremental bundle changed and contained the probe, and after the revert the next incremental APK was byte-identical to D3. The fingerprint covers app.json and its assets, package and lock files, plugins, patches, native module sources, credentials (hash), both build scripts, ABIs, Node, JAVA_HOME, ANDROID_HOME and every `EXPO_*` variable except `EXPO_PUBLIC_*` (bundle-only, and the bundle task always reruns). Residual risk: a hand edit inside `node_modules/<pkg>/android` without a patch file is not seen. Over the audit window's 31 clean test builds the saving would be about 4.4 h [inferred]. Owner-approved 2026-10-07 (commit `ca0b0f5`).
- **E1 (ANDR-002): bytes pass, time unproven.** A vs B: the bundle and all 947 entries present in both APKs are byte-identical, including every `lib/arm64-v8a/*.so`, `classes*.dex`, `resources.arsc` and the manifest; the only difference is 20 `lib/x86_64/*` entries. Time: −237 s median, but the null spread is 429 s and pair 3 inverted (480 vs 527 s), so it is not a demonstrated saving. Resolution named by the report: 3 more pairs on a quiet host, or Gradle CPU time. Owner-approved on the byte evidence.
- **Pixel guard (both):** failed as pre-registered on 3 of 6 shots, but B and D, byte-identical files, failed the same shots by the same amounts (hint pulse, test banner), so it measured the instrument, not the build. Bytes decide.
- **Store builds** were out of scope and keep `armeabi-v7a,arm64-v8a` and the clean recipe (STORE-002).

## Stale artifacts
- block-blaster: `./gradlew … | tail -5` reported the pipe's exit code, so BUILD FAILED surfaced as exit 0 and a 2-hour-stale APK was installed and re-tested as if it were the fix.
- geoguesser-app: the same pipe hid a successful build; a redundant second build was started on top of it.
- arrows-game 2026-09-29: the shell resolved `node` to v14; `expo prebuild` warned but exited 0, Gradle failed, and the script copied the previous AAB under the new version name (same sha256). Rules adopted: pin Node, check `android/app/build.gradle` exists after prebuild, exit on Gradle failure before copying, compare the output sha with the previous build.
