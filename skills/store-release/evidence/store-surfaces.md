# Store surfaces: Play-only flows, screenshots, policy text

**Source:** arrows-game memory `w4-11-store-review-gotchas.md` (2026-09-26), `w3-15-w7-09-gotchas.md` (2026-10-06); arrows-game reports W4-11, W7-06 (2026-09-26), W7-09 (2026-10-06); geoguesser-app memory `tester-feedback-2026-09-07.md`, `android-package-is-frozen.md` (2026-08-28); snaxx-tech memory `apps-contain-unity-ads.md` (2026-07-18); block-blaster memory `interstitial-on-game-over.md` (2026-07-27), `blockrow-to-block-destroy-rename.md`.

## Play-only flows
- arrows-game W4-11: the emulator's Play Store is a stub; `requestReview` rejected in 8–80 ms ("Failed to bind"); `isAvailableAsync` returned true after 7 ms yet nothing showed. `expo-store-review` 57.0.3 `isAvailableAsync` means "Play package installed", not what the docs say.
- geoguesser-app 2026-09-07: the In-App Review dialog can only be seen on a Play-installed build.

## Screenshots
- Play (read 2026-10-06): JPEG or 24-bit PNG without alpha, long side ≤ 2× short side, 320–3840 px. Emulator `screencap` writes RGBA: prove alpha is 255 everywhere, then save RGB. W7-09 captured at `wm size 1440x2880`, used SystemUI demo mode, and used OCR to reject any frame showing "Test Ad".

## Policy and listing text
- snaxx-tech: the privacy policy claimed "no ads SDKs / no advertising identifiers / data never leaves device", which was false per the binary; rewritten to disclose the SDK.
- block-blaster: adding an interstitial made five store, privacy and in-app copy claims false at once.
- arrows-game W7-06: data-safety evidence taken from the built AAB via bundletool (12 `uses-permission` names, versionCode 10, minSdk 24, targetSdk 36).
- geoguesser-app and block-blaster: once a Play listing exists, the applicationId is permanent; only the display name may change.
