# Readiness before input, and shell gotchas

**Source:** arrows-game `docs/engineering-lessons.md` (W7-09 and W3-21 2026-10-06; HALLOWEEN-PLUS 2026-10-07; ART-SKINS-07 "Capture input must have fresh, settled evidence"); arrows-game memory `admob-b-emulator-gotchas.md` (2026-09-24), `polish-t11-gate-gotchas.md` (2026-09-25), `w4-07-hermes-fold-and-boot-trace.md`, `w4-11-store-review-gotchas.md`, `polish-t6-handoff-and-gotchas.md`, `w5-02-08-harness-gotchas.md`; block-blaster memory `animation-gated-visibility.md` (2026-09-08); geoguesser-app `docs/engineering-lessons.md` L6, `docs/plan/evidence/device-2026-10-07/scripts/c-art4b2.sh`, `c/reminder/RESULT.md` (2026-10-08).

## Wrong-screen input (measured)
- 2026-10-06 W7-09: with a Google test interstitial showing, `dumpsys window` still printed `mCurrentFocus=…MainActivity` while `dumpsys activity activities` showed `mResumedActivity` = `AdActivity`; a focus-only guard let a screenshot capture the ad. The driver now requires the resumed activity.
- 2026-10-07 HALLOWEEN-PLUS: on a loaded host a tap sent while the hierarchy dump was slow landed late and opened a different book tile.
- 2026-09-24 ADMOB-B: calibrated blind taps ran out of hearts and clicked through a test rewarded ad (3 `aclk` lines).
- 2026-09-25 POLISH-T11: after an app crash, scripted taps landed on the launcher and opened another app; guard = focus check before every input.
- ART-SKINS-07: a failed `uiautomator dump` left the previous XML in place; a boot-completed property did not mean the package services were ready.
- block-blaster 2026-09-08: `input tap …; input keyevent HOME` never delivered the tap; two fixes were built against a phantom repro.
- geoguesser-app 2026-10-08 (ART-4b, API 36 AVD): "the app went back to the launcher, no log line" was a native SIGSEGV in librnskia, visible only in `logcat -b crash`. The drivers now clear the crash buffer at start and check it after every step, failing fast on an entry for the app (`scripts/c-art4b2.sh` `crashed()`); a later run ended "crash buffer clean for the app".
- geoguesser-app 2026-10-08: a label match for the app's name hit the launcher's "Predicted app" row; on a cold-booted AVD `dumpsys window` printed nothing, so focus is read from `dumpsys activity activities` `topResumedActivity` (as W7-09 above).

## zsh word splitting (4 incidents, arrows-game 2026-09-24..27)
- a mutation check silently ran 0 tests (`set -- $w`);
- `repack.sh $CAP` passed the whole flag set as one argument, so the test-ads flag was unset and production ad units entered the bundle; the bundle proof caught it before install;
- `tar -cf x.tar $FILES` omitted six sources before they were overwritten (recovered from scratch copies);
- a `for f in $F` swap loop did nothing.
macOS ships bash 3.2: no `mapfile`, no `declare -A`.
