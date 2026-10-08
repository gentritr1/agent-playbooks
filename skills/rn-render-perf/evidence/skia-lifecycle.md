# Skia 2.2.12 and Reanimated 4.1: unmount crash (REND-001) and source-read facts

**Source:** geoguesser-app `docs/engineering-lessons.md` L3, L4 (2026-10-08); geoguesser-app `docs/plan/evidence/art-4b/crash-1045/crash-buffer.txt`; geoguesser-app memory `skia-write-after-unmount-segfaults.md`; geoguesser-app `docs/plan/evidence/device-2026-10-07/c/art4b2-1212/summary.txt`; installed sources in the geoguesser art-4s tree: `@shopify/react-native-skia` 2.2.12, `react-native-reanimated` 4.1.7, `react-native-worklets` 0.5.1 (lines re-read 2026-10-08); arrows-game `patches/@shopify+react-native-skia+2.6.2.patch`.

## The crash
- Device, 2026-10-08, API 36 arm64 AVD: `Fatal signal 11 (SIGSEGV) … Cause: null pointer dereference`, top frame `librnskia.so … RNSkia::RNSkJsiViewApi::setJsiProperty`, reached through `ViewRegistry::withViewInfo` from libworklets on the main thread, about 200 ms after an entrance layer logged a skip and unmounted.
- At that commit 4,307 tests and three reviews were green: a headless fake cannot segfault.
- Source, `cpp/rnskia/RNSkJsiViewApi.h` (2.2.12): `withViewInfo` (lines 45–56) creates and stores an empty `RNSkViewInfo` for an id it does not know; the `onSize` branch of `setJsiProperty` (lines 105–111) calls `info->view->getScaledWidth()` with no null check, while the other branch checks `info->view != nullptr` (line 119).
- `cpp/api/JsiSkHostObjects.h` lines 91–94: `dispose` is "a no-op on native"; memory returns only through GC, so disposing does not make a late write safe.
- Fix that shipped: no `onSize` prop (poll the null-safe `SkiaViewApi.size(nativeId)`); writes gated on a UI-thread `alive` flag and a non-zero native size; unmount = one `runOnUI` stop job, an ack after one more UI frame, then React unmounts; the test fake of the registry THROWS on writes to dropped views. 18 new tests were red on the crashing commit.
- Device side of the fix: the crash buffer stayed clean after it (cold starts and 4 replays, 12:12 run), but every replay in that run logged a skip and both mid-spin checks were void ("NO SPIN STARTED"), so the crashing path was not re-exercised on the device.
- Second project: arrows-game patched the same registry in Skia 2.6.2 ("Ignore property updates that race with unmount instead of recreating a global registry entry that retains the old SkPicture forever"; a read-only `getView` lookup). Its motive was retention, not a crash; whether 2.6.2's `onSize` branch is null-safe was not checked.

## Source-read facts, installed 2.2.12 / 4.1.7 (evidence only; REND-002 retired in the v0.5.0 review, see `retired/`)
One project's source reading with no measured number: read these lines again for your installed version (LOOK-002) before relying on any of them.

| Behaviour | Where | Consequence |
|---|---|---|
| A shared-value write equal to the current value returns early ("prevent setting again to the same value") | `react-native-reanimated/src/valueSetter.ts` lines 80–84 | writing the same mutated Paint object again never triggers mappers; alternate two Paints |
| `<ImageShader sampling>` without cubic B/C calls `image.makeShaderCubic(tx, ty, filter, mipmap, lm)` | `src/sksg/Recorder/commands/Shaders.ts` lines 218–224 | `FilterMode.Linear` (1) and `MipmapMode.None` (0) become cubic B = 1, C = 0; build the child shader with `image.makeShaderOptions(…, FilterMode.Linear, MipmapMode.None)` |
| `Skia.Data.fromURI` resolves only inside the stream callback; `performStreamOperation` returns early when the Java stream is null | `cpp/api/JsiSkDataFactory.h` lines 18–43; `android/cpp/jni/JniPlatformContext.cpp` lines 147–150 | an unresolvable URI never settles on Android; wrap it in a timeout |
| `setOpaque(true)` replaces the `SkiaTextureView` with a `SkiaSurfaceView` | `android/…/SkiaBaseView.java` lines 23–33 | a SurfaceView draws outside the app's HWUI pipeline, so gfxinfo stops seeing the Canvas's frames (stated in L4; not separately measured) |

None of these four was isolated in a device run; the ART-4b brief and code were written to them.
