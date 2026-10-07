# Release recipe and clean binaries

**Source:** arrows-game `docs/process/speed-audit-2026-10-07.md` §(d) "What not to change"; arrows-game memory `shared-host-contention.md` (Node drift 2026-09-29), `art-skins-01-review.md` (2026-09-30), `reward-path-2026-10-04.md`; arrows-game `docs/engineering-lessons.md` ("Spike assets must never be packaged unconditionally", "A killed build runner leaves diagnostics in the product tree"); geoguesser-app memory `commit-before-release-build.md` (2026-09-07), `geoguesser-release-build-steps.md` (2026-09-18); block-blaster memory `release-keystore-setup.md` (2026-07-18).

## Recipe (kept clean on purpose)
- arrows-game speed audit: release and Play AABs keep `prebuild --clean`, `armeabi-v7a,arm64-v8a`, upload signing, and version-code and sha checks (6 builds, 1.03 h); this is not an optimisation target.
- geoguesser-app 2026-09-07: release 1.3.1 (10) was built from an uncommitted tree; a week after upload "Nothing in git corresponded to the binary testers were running." Rule: commit and tag the exact tree first.
- geoguesser-app 2026-09-18: clean build (7 min), then diff the new AAB against the previous one: same package and upload-cert SHA-256, identical permissions and ad-unit strings.
- arrows-game 2026-09-29: `node` resolved to v14; prebuild warned but exited 0, Gradle failed, and the script copied the previous AAB under the new version name (same sha256).
- block-blaster: with a prebuild-generated `android/`, signing edits are lost on `prebuild --clean`; keep the keystore backed up outside the repo and enrol in Play App Signing.

## No experiment code in shipped binaries
- ART-SKINS-01 (2026-09-30): a spike added an artifacts directory as an unconditional Gradle asset source; the default-OFF flag did not stop packaging (inferred from the Gradle line and the spike APK's asset list). Practice: gate assets on the same build flag and list APK assets in the OFF check.
- HALLOWEEN-01 (2026-10-04): a contract runner injects diagnostic classes and restores them in `finally`; the session was killed, SIGKILL skipped `finally`, and ten diagnostic classes stayed in the product module. The build script now refuses to start while they exist, the APK proof rejects an `instrumentation` manifest entry, and long runners run under `nohup`.
