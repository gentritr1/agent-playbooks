---
name: android-builds-devices
description: Use before Gradle or prebuild runs, test APK builds or installs, adb on emulators or devices, capture harnesses, or work on a shared host.
---

# Android builds and devices

Measured on a shared macOS host running several agent sessions. Gates say what must hold when you finish.

### ANDR-001 · One serial, one owner
- **Rule:** Address every adb call with `-s <serial>`, and let one agent own a device at a time.
- **Kind:** invariant — why: other sessions and sibling agents drive the same emulators and invalidate each other's runs.
- **Evidence:** arrows-game 2026-09-26: two subagents killed each other's app on one emulator; a bare `adb reconnect` bounced another session's emulator → [shared-host](evidence/shared-host.md)
- **Confidence:** VERIFIED
- **Gate:** `grep -nE '\badb\b' <scripts> | grep -v -- '-s '` prints nothing; logcat shows no foreign app launch during the run
- **Valid while:** `ctx:android` · shared host · last_validated: 2026-09-30
- **Source:** ANDR-001

### ANDR-002 · Test APKs carry only the device ABI
- **Rule:** Build test APKs for `arm64-v8a` only; release bundles keep `armeabi-v7a,arm64-v8a`.
- **Kind:** fact — every AVD and phone in use is arm64-v8a; dropping x86_64 leaves the arm64 contents byte-identical, so it only skips work.
- **Evidence:** arrows-game 2026-10-07 E1 (owner-approved on the bytes): all 947 shared entries identical, only 20 `lib/x86_64` removed; time 835 → 598 s median, inside a 429 s null spread, one pair inverted → [build-time](evidence/build-time.md)
- **Confidence:** VERIFIED — bytes, 2 pairs; the time saving is INFERRED (unproven on a loaded host)
- **Gate:** `unzip -l test.apk | grep -c 'lib/x86'` is 0; the release bundle lists both arm ABIs
- **Valid while:** `ctx:android` · arm64 AVDs and phone · last_validated: 2026-10-07
- **Source:** ANDR-002

### ANDR-003 · Skip the clean rebuild while native inputs are unchanged
- **Rule:** Build test APKs incrementally while a fingerprint of every native input equals the last successful build's stamp; a mismatch, missing stamp or failed build means clean. Store builds always build clean (STORE-002, invariant).
- **Kind:** heuristic — goal: minutes per test build at identical bytes; override: stronger case evidence, stated in the report; expires: 2027-01-05
- **Evidence:** arrows-game 2026-10-07 E3 (owner-approved): 598 → 88 s median, null spread 133 s, 3 of 3 pairs faster; 3 of 3 APKs byte-identical; Kotlin edit forced clean, TS edit stayed incremental → [build-time](evidence/build-time.md)
- **Confidence:** VERIFIED — interleaved, replicated, byte-checked
- **Gate:** before adoption, incremental APK sha256 equals a clean build of the same tree, with a native-edit control that forces clean; release logs show `prebuild --clean`
- **Valid while:** `expo@57` `react-native@0.86` · hand edits in `node_modules/*/android` unseen · last_validated: 2026-10-07
- **Source:** ANDR-003

### ANDR-004 · Measure free disk right before the heavy step
- **Rule:** Check free disk immediately before each native build, install batch or worktree fan-out.
- **Kind:** invariant — why: other sessions consume disk mid-task, and ENOSPC kills builds and checks partway.
- **Evidence:** arrows-game: 11 → 1.8 GB in 2 h; cold Gradle needs ~7 GB; ENOSPC in 4 projects → [shared-host](evidence/shared-host.md)
- **Confidence:** VERIFIED
- **Gate:** the build log prints free space ≥ 7 GB (cold) taken within a minute of the build start
- **Valid while:** `ctx:android` · shared macOS host · last_validated: 2026-10-05
- **Source:** ANDR-004

### ANDR-005 · Success is the build's own exit code and a new artifact
- **Rule:** Read the build's own exit status, unpiped, and prove the artifact is new before installing it.
- **Kind:** invariant — why: a stale artifact gets tested as if it were the fix.
- **Evidence:** block-blaster: `| tail` turned BUILD FAILED into exit 0 and a 2-hour-old APK was installed; arrows-game 2026-09-29: the previous AAB was copied under a new version (same sha256) → [build-time](evidence/build-time.md)
- **Confidence:** VERIFIED
- **Gate:** `pipefail` or no pipe; artifact sha256 differs from the previous build and its mtime is after the build start
- **Valid while:** `ctx:android` · last_validated: 2026-09-29
- **Source:** ANDR-005

### ANDR-006 · Input only on a proven screen
- **Rule:** Before each input or capture, prove the expected screen from fresh runtime state.
- **Kind:** invariant — why: input on the wrong screen taps ads, buys the wrong item or records false evidence.
- **Evidence:** arrows-game 2026-10-06: focus said MainActivity while a test ad was resumed; a late tap opened the wrong book tile; 2026-09-24: blind taps clicked a test ad → [readiness](evidence/readiness.md)
- **Confidence:** VERIFIED
- **Gate:** the driver log shows the app's resumed activity and its own state log line before every input
- **Valid while:** `ctx:android` · API 31 emulator · last_validated: 2026-10-07
- **Source:** ANDR-006

### ANDR-007 · Device and build scripts are bash, not zsh
- **Rule:** Write multi-step device and build scripts as bash files with arrays.
- **Kind:** fact — zsh does not word-split `$VAR`; macOS bash is 3.2 (no `mapfile`, no `declare -A`).
- **Evidence:** arrows-game 2026-09-24..27: a mutation check ran 0 tests; a flag set passed as one argument put production ad ids in a bundle → [readiness](evidence/readiness.md)
- **Confidence:** VERIFIED
- **Gate:** scripts start `#!/bin/bash` and `set -euo pipefail`; `bash -n` passes
- **Valid while:** macOS default zsh, bash 3.2 · last_validated: 2026-09-27
- **Source:** ANDR-007

## Gates before you report done
Serial and owner (001), ABI list (002), disk printed (004), exit code and new sha (005), resumed activity before input (006). A benchmark build's flags are asserted from a runtime log line (TEST-005).

## Not covered / defer to
Expo config and modules: `expo:*`. Store bundles and ad proofs: `store-release`. Perf statistics: `testing-gates`.
