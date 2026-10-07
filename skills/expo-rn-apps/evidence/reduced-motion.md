# Reduced motion: measured failures and the device check

**Source:** arrows-game memory `shipping-defects-found-2026-09-09.md`; arrows-game `docs/engineering-lessons.md` ("Decorative Reanimated timing still needs an explicit reduced-motion policy", REWARD-01, 2026-10-04; ART-SKINS-02 "Motion evidence rule"); arrows-game report `docs/next-level/reports/P-02.md` (2026-09-19); geoguesser-app memory `reduced-motion-delayed-entering-hides-view.md` (2026-09-16).

| Project, date | Observation | Numbers |
|---|---|---|
| arrows-game 2026-09-09 | Every feedback `withTiming` used the default `ReduceMotion.System`; with the OS setting on, progress jumped to 1 | blocker opacity 0, bump 0, hint pulse amplitude 0: the paid hint rendered nothing |
| arrows-game 2026-09-19 (P-02) | The perf harness itself ran with animation scales 0, so it measured the reduced-motion path | scales `0 0 0`: 0 flash px; `1 1 1` after force-stop + relaunch: 2371 px |
| arrows-game 2026-10-04 (REWARD-01) | Component tests passed; the repo-wide policy audit failed on two `withTiming` configs without a policy | fixed, then 126 suites / 2,116 tests; device capture at scale 0 showed the reveal without sparkles |
| geoguesser-app 2026-09-16 | A delayed Reanimated `entering` with animations off left the view invisible | blank on 4 of 5 fresh installs; 0 of 5 after removing the `entering` |

**Device method (verified, arrows-game):** Reanimated on Android reads `transition_animation_scale == 0` once at process start. Set the scale, force-stop, relaunch, capture, and restore the original value in a `finally`. Changing only `animator_duration_scale` is not enough.

**Why a static stand-in:** a shorter animation still shows nothing at progress 1. The fix that shipped kept a static blocker state for reduced-motion players.
