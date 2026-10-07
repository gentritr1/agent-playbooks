# Headless checks that passed on a broken screen

**Source:** `~/.claude/CLAUDE.md` §6 red flags; geoguesser-app memory `never-read-nativeevent-inside-a-state-updater.md` (2026-09-30), `web-previews-show-fallback-fonts.md` (2026-10-06); arrows-game memory `w4-10-menu-compose-gotchas.md` (2026-09-26), `w5-art-batch-gotchas.md` (2026-09-27); lucky-shelf memory `fabric-transform-gotchas.md` (2026-07-11); tondo memory `sampled-viewport-gate-blind-spot.md`; form-studio memory (2026-10-02, responsive check).

| Project | What passed | What was broken |
|---|---|---|
| geoguesser-app 2026-09-30 | task review, re-review, tsc, 521 tests, `npm run check`, a QA build | `event.nativeEvent` read inside a `setState` updater: FATAL on every round start, on device for 10 days |
| arrows-game 2026-09-26 | jest and uiautomator bounds | a transparent wrapper drawn after the header ate its taps; only an adb tap plus a DB read caught it (fix `pointerEvents="box-none"`) |
| arrows-game 2026-09-27 | jest | `<Image source={require(png)} style={absoluteFill}>` drew at the source size in a corner; only the emulator capture caught it |
| lucky-shelf 2026-07-11 | tsc and vitest | Fabric collapsed separate `scaleX`/`scaleY`; a `with*()` result used in arithmetic gave NaN every frame; caught by simulator screenshot |
| geoguesser-app 2026-10-06 | web preview screenshots | text rendered in a browser serif fallback; the owner judged "the new font" on it |

## Sampled viewports
- tondo: a gap gate sampling 1024×768, 1280×800 and 1440×900 was green; sweeping the band found 1366×768 at −2.5 px and 1280×740 at −5.9 px. A single-digit clearance was the tell.
- form-studio: a check sampling 375 and 1440 missed a control row that broke at 900–1240 px; the owner found it. The fix sweeps 320/375/620/768/925/1100/1240/1440 and tests label overflow.
