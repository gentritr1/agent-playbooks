# EXPO_PUBLIC values are build-time constants

**Source:** geoguesser-app memory `gradle-bundle-ignores-expo-public-env.md` (2026-09-16); arrows-game memory `w6-01-mask-rebuild-and-trace-gotchas.md` (2026-09-17), `remote-config-emulator-gotchas.md` (2026-09-17); arrows-game report `docs/next-level/reports/ADMOB-B.md` (2026-09-24); block-blaster memory `env-fail-closed-ads.md` (2026-09-02).

- geoguesser-app: after an `EXPO_PUBLIC_*` change with no source edit, the Gradle bundle task reported `UP-TO-DATE`; the store artifact carried the QA bundle (identical sha256). Fix: declare an env digest as a task input and stamp the artifact. Reproduced and fixed.
- arrows-game W6-01: `npx expo export` after flipping a flag reused Metro's transform cache; the positive-control grep read 0 until `--clear`.
- arrows-game W6-02: `process.env.EXPO_PUBLIC_X ?? ''` is inlined (bundle grep count 1), contrary to a docs summary.
- arrows-game ADMOB-B: `./gradlew --stop` before a build whose bundle depends on an `EXPO_PUBLIC` value; a daemon holds the old environment.
- block-blaster: fixing `.env` after building changes nothing in the shipped bundle.

**Counting bytes in a Hermes bundle (contradiction resolved):** block-blaster memory says grep finds nothing in Hermes bundles; geoguesser-app found `strings | grep -c` gave false zeros (it counts lines) while a raw byte count worked; arrows-game ADMOB-B and PETAL-ADS-01 (2026-10-05) count both UTF-8 and UTF-16LE (a string with `·` is stored UTF-16LE). Newer, positive-controlled evidence wins: count raw bytes in both encodings and require a known-present control string first.
