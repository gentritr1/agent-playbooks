#!/bin/bash
set -euo pipefail
cat > runs.csv <<'CSV'
order,arm,frame_p95_ms
1,OFF,18.9
2,ON,19.6
3,NULL,19.9
4,OFF,19.8
5,ON,19.1
6,NULL,19.4
7,OFF,18.6
8,ON,19.7
9,NULL,20.1
10,OFF,19.4
11,ON,20.3
12,NULL,19.0
CSV
cat > NOTES.md <<'MD'
OFF = base build, ON = the change, NULL = a second install of the base build (same APK), run interleaved on one emulator.
A previous reviewer wrote: "ON run 11 (20.3 ms) is outside the OFF range, so the change regresses."
MD
