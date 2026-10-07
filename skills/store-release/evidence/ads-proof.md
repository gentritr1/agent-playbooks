# Test-ads proof and ad-creative handling

**Source:** arrows-game reports ADMOB-A (2026-09-23), ADMOB-B (2026-09-24), PETAL-ADS-01 (2026-10-05), W2-04 (2026-09-24), W2-05; arrows-game memory `w4-11-store-review-gotchas.md` (2026-09-26), `admob-b-emulator-gotchas.md`, `w2-04-scrim-capture-gotchas.md`, `w2-05-capture-gotchas.md`; arrows-game `docs/engineering-lessons.md` (PETAL-ADS-01 entry); geoguesser-app memory `large-screen-landscape-is-live.md`; block-blaster memory `hermes-bundle-not-greppable.md`.

## Bundle proof
- ADMOB-A: "The 'Test Ad' label alone does not prove TestIds on an emulator. The proof is the bundle grep."
- ADMOB-B: Hermes bundle counted in ASCII and UTF-16LE with a positive control compiled via `hermesc -O`: production units 0 / 0 each; the Google sample publisher id 9 times. Logcat showed 3 "This request is sent from a test device" lines, one per unit.
- W4-11 (2026-09-26): a zsh word-splitting bug passed the flag set as one argument, so the test-ads flag was unset and production units entered the bundle; the proof caught it before install.
- PETAL-ADS-01: a string containing `·` is stored UTF-16LE in Hermes; the positive control counted [0, 1] across the two encodings, so proofs must count both.
- geoguesser-app: a release build with an empty test-device list requests real units, which is invalid traffic on an emulator.
- block-blaster: alternative proof through UI that renders only when the value exists ("costs zero ad impressions").

## Creatives
- PETAL-ADS-01 (2026-10-05): Google's rewarded test unit ignored BACK while it showed "Reward in 4 seconds"; BACK one second before the reward still earned it (+3). "Dismissed early grants nothing" cannot be produced on device with BACK; it is covered by a fake-SDK test (`CLOSED` without `EARNED_REWARD`) and the device check is UNVERIFIED.
- W2-04: the test interstitial ignores BACK; close = the X after its countdown, never the creative.
- W2-05: rewarded test creatives vary and the X position is not fixed; BACK after ~32 s worked (0 clicks); a blind coordinate tap once closed a creative on blank space by luck.
- ADMOB-B: calibrated blind taps clicked through a test rewarded ad (3 `aclk` lines).
