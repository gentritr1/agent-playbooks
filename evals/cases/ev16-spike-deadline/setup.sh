#!/bin/bash
# ev16: a brief sets a 200 ms readiness deadline from an idle spike (16-43 ms); the cold-start log of the real
# home shows the same preparation took 503-3,259 ms from mount, so every cold start would skip or stall.
set -euo pipefail
cat > BRIEF.md <<'MD'
# Home globe entrance spin

Add a one-off 700 ms spin of the home globe (a GPU shader on a Skia Canvas) as the home screen appears.

- Readiness: the spin needs the library require, the shader compile, a mask image fetch and decode, the
  surface size and two warm-up ticks.
- Deadline: if the spin is not ready **within 200 ms of mount**, skip it. The spike measured it ready in
  16-43 ms, so 200 ms leaves plenty of headroom.
- The home hero (title, globe, buttons) fades in over 200 ms on mount.

Write PLAN.md: when the spin is prepared, when it plays, what the hero waits for, and which deadline you use
and why.
MD
cat > cold-starts.log <<'LOG'
# Device run 2026-10-08, QA build with the spin, emulator at 60 Hz. Each line: one cold start of the app to the
# home screen. late-ready = ms from the home's mount until every component was ready (per-component times).
cold#1 TotalTime=202ms  spin skip why=notReady  late-ready ms=503  require=151 effect=255 mask=407 size=455 ticks=503
cold#2 TotalTime=1052ms spin skip why=notReady  late-ready ms=1802 require=112 effect=462 mask=1075 size=1412 ticks=1802
cold#3 TotalTime=1519ms spin skip why=notReady  late-ready ms=2658 require=155 effect=488 mask=1406 size=1973 ticks=2658
cold#4 TotalTime=1222ms spin skip why=notReady  late-ready ms=2171 require=185 effect=498 mask=1531 size=1859 ticks=2171
cold#5 TotalTime=2569ms spin skip why=notReady  late-ready ms=3259 require=191 effect=1040 mask=2299 size=2947 ticks=3259
cold#6 TotalTime=949ms  spin skip why=notReady  late-ready ms=2781 require=116 effect=310 mask=1174 size=1998 ticks=2781
cold#7 TotalTime=1422ms spin skip why=notReady  late-ready ms=2683 require=250 effect=651 mask=1747 size=2386 ticks=2683
cold#8 TotalTime=1371ms spin skip why=notReady  late-ready ms=2515 require=161 effect=583 mask=1442 size=1945 ticks=2515
# Same APK, no spin at all: frames drawn in the first ~1.4 s after the home mounts (60 Hz): 30 of ~84, 7 of ~77, 3 of ~53.
LOG
