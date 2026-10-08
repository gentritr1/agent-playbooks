# Reduced motion: measured failures and the device check

**Source:** arrows-game memory `shipping-defects-found-2026-09-09.md`; arrows-game `docs/engineering-lessons.md` ("Decorative Reanimated timing still needs an explicit reduced-motion policy", REWARD-01, 2026-10-04; ART-SKINS-02 "Motion evidence rule"); arrows-game report `docs/next-level/reports/P-02.md` (2026-09-19); geoguesser-app memory `reduced-motion-delayed-entering-hides-view.md` (2026-09-16), `device-evidence-was-reduced-motion-only.md` (2026-10-08); geoguesser-app `docs/plan/evidence/device-2026-10-07/c/snd1-RESULT.md`, `docs/engineering-lessons.md` L8; arrows-game `docs/perf-harness.md` Rule 1 (2026-09-17).

| Project, date | Observation | Numbers |
|---|---|---|
| arrows-game 2026-09-09 | Every feedback `withTiming` used the default `ReduceMotion.System`; with the OS setting on, progress jumped to 1 | blocker opacity 0, bump 0, hint pulse amplitude 0: the paid hint rendered nothing |
| arrows-game 2026-09-19 (P-02) | The perf harness itself ran with animation scales 0, so it measured the reduced-motion path | scales `0 0 0`: 0 flash px; `1 1 1` after force-stop + relaunch: 2371 px |
| arrows-game 2026-10-04 (REWARD-01) | Component tests passed; the repo-wide policy audit failed on two `withTiming` configs without a policy | fixed, then 126 suites / 2,116 tests; device capture at scale 0 showed the reveal without sparkles |
| geoguesser-app 2026-09-16 | A delayed Reanimated `entering` with animations off left the view invisible | blank on 4 of 5 fresh installs; 0 of 5 after removing the `entering` |
| geoguesser-app 2026-10-08 (SND-1) | The cue-loss evidence log and all 5 rendered tests ran with reduced motion (animator scale 0); review found that with animations ON the cue fired at resume during the post-ad re-warm and was lost | the device re-run then covered both: run A at scale 0 and run B at all three scales 1, the cue played exactly once after the ad in each; the defer path itself stayed unit-test-only |

**Device method (verified, arrows-game):** Reanimated on Android reads `transition_animation_scale == 0` once at process start. Set the scale, force-stop, relaunch, capture, and restore the original value in a `finally`. Changing only `animator_duration_scale` is not enough.

**Why a static stand-in:** a shorter animation still shows nothing at progress 1. The fix that shipped kept a static blocker state for reduced-motion players.
