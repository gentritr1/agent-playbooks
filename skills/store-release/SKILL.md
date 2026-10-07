---
name: store-release
description: Before release AAB, test-ads builds or installs, Play screenshots, listing, privacy or data-safety text, or Play-only flows.
---

# Store release and ads

Release steps are invariants: the recipe itself is the gate. Every outward step (upload, submit, publish) needs the owner's explicit yes each time.

### STORE-001 · Prove test ads from the bundle before any install
- **Rule:** Before installing a non-release build, prove from its bundle that test ad ids are present and production ids are absent.
- **Kind:** invariant — why: real ad traffic from development devices is invalid traffic and risks the ad account.
- **Evidence:** arrows-game 2026-09-24: production ids 0/0, test publisher 9; 2026-09-26: a zsh flag bug put production units in a bundle and the proof caught it; the "Test Ad" label is not proof → [ads-proof](evidence/ads-proof.md)
- **Confidence:** VERIFIED
- **Gate:** byte counts in UTF-8 and UTF-16LE: test id ≥1, every production id 0, a known-present control string ≥1
- **Valid while:** `ctx:ads` · Hermes bundles · last_validated: 2026-10-05
- **Source:** STORE-001

### STORE-002 · The release recipe is fixed and provable
- **Rule:** Build releases only from a committed, tagged tree with the clean recipe, and diff the result against the previous release.
- **Kind:** invariant — why: an untraceable or stale binary reached testers and the store.
- **Evidence:** geoguesser 2026-09-07: no commit matched the testers' binary; arrows-game 2026-09-29: a failed build copied the previous AAB under a new version (same sha256) → [release-recipe](evidence/release-recipe.md)
- **Confidence:** VERIFIED
- **Gate:** `git describe --exact-match` names the build tree; a clean build (`prebuild --clean` where `android/` is generated); both arm ABIs; upload certificate matches; versionCode increased; sha256 differs from the previous AAB
- **Valid while:** `ctx:android` · Play App Signing · last_validated: 2026-10-01
- **Source:** STORE-002

### STORE-003 · Never touch an ad creative
- **Rule:** Close test ads only by BACK or the close control after its countdown, and cover early-dismiss paths with a fake-SDK test.
- **Kind:** fact — Google test interstitial and rewarded ads ignore BACK until the countdown or reward completes.
- **Evidence:** arrows-game 2026-10-05: BACK one second before the reward still earned it; 2026-09-24: blind taps clicked a test ad (3 `aclk`) → [ads-proof](evidence/ads-proof.md)
- **Confidence:** VERIFIED
- **Gate:** logcat shows 0 ad clicks; the early-dismiss case is a unit test, device check marked UNVERIFIED
- **Valid while:** `react-native-google-mobile-ads@17.1` · Google test units · last_validated: 2026-10-05
- **Source:** STORE-003

### STORE-004 · Play-only flows are unverified until a Play install
- **Rule:** Mark in-app review and other Play-distributed flows UNVERIFIED-DEVICE until tested from an internal test track.
- **Kind:** fact — on a sideloaded or emulator build the Play service binding fails or nothing shows.
- **Evidence:** arrows-game 2026-09-26: review bind failed in 8–80 ms on the emulator; geoguesser 2026-09-07: the review dialog appeared only on the Play-installed build → [store-surfaces](evidence/store-surfaces.md)
- **Confidence:** VERIFIED
- **Gate:** the report labels the flow UNVERIFIED-DEVICE or cites an internal-track run
- **Valid while:** `expo-store-review@57` · last_validated: 2026-09-26
- **Source:** STORE-004

### STORE-005 · Shipped binaries carry no experiment or diagnostic code
- **Rule:** Gate experiment assets on the same build flag as their code, and refuse a build while diagnostic files sit in the product tree.
- **Kind:** invariant — why: a default-OFF flag did not stop packaging, and a killed runner skipped its cleanup.
- **Evidence:** arrows-game 2026-09-30: a spike asset directory was packaged into every build; 2026-10-04: SIGKILL left ten diagnostic classes in the product module → [release-recipe](evidence/release-recipe.md)
- **Confidence:** VERIFIED
- **Gate:** the APK asset list equals the baseline; the manifest has no `instrumentation`; the preflight diagnostic-file check passes
- **Valid while:** `ctx:android` · last_validated: 2026-10-04
- **Source:** STORE-005

### STORE-006 · Store text matches the shipped binary
- **Rule:** Derive privacy, data-safety and listing claims from a dump of the release binary, and re-check them when an SDK or ad format changes.
- **Kind:** invariant — why: policy text claimed no ad SDKs while the apps contained one.
- **Evidence:** snaxx-tech: the policy said "no ads SDKs", false per `aapt2`; block-blaster: five copy claims became false when an interstitial landed; Play screenshots must have no alpha → [store-surfaces](evidence/store-surfaces.md)
- **Confidence:** VERIFIED
- **Gate:** data-safety list equals the bundletool permission dump; screenshots are RGB with long side ≤ 2× short
- **Valid while:** Google Play policy as read 2026-10-06 · last_validated: 2026-10-06
- **Source:** STORE-006

## Gates before you report done
Ads proof counts (001); release recipe checklist (002); 0 ad clicks (003); Play-only flows labelled (004); asset list and manifest (005); store text from the dump (006).

## Not covered / defer to
EAS submit and store metadata: `expo:eas-app-stores`. Deploy checklists: `engineering:deploy-checklist`.
