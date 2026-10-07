---
name: demo-skill
description: Use when testing the playbook lint; fixture only.
---

# Demo skill

### DEMO-001 · Name the device on every call
- **Rule:** Pass the device serial to every device command.
- **Kind:** invariant — why: a second device on the host receives unqualified commands.
- **Evidence:** fixture project, 2026-09-26: two agents drove one device → [ev](evidence/demo.md)
- **Confidence:** VERIFIED
- **Gate:** `grep -L -- '-s ' scripts/*.sh` prints nothing
- **Valid while:** `ctx:android` `claude-code@2.1` · last_validated: 2026-10-01
- **Source:** DEMO-001

### DEMO-002 · Build only the ABI the devices run
- **Rule:** Test builds compile only the device ABI.
- **Kind:** fact — both fixture devices are arm64.
- **Evidence:** fixture, 2026-10-07: 7.7 vs 3.5 min → [ev](evidence/demo.md)
- **Confidence:** VERIFIED
- **Gate:** `unzip -l app.apk | grep lib/` lists one ABI
- **Valid while:** `react-native@0.85|0.86` · last_validated: 2026-10-01
- **Source:** DEMO-002

### DEMO-003 · Skip a clean rebuild when native inputs are unchanged
- **Rule:** Reuse incremental builds while the native fingerprint is unchanged.
- **Kind:** heuristic — goal: shorter test builds with identical output; override: stronger case evidence, stated in the report; expires: 2026-12-30
- **Evidence:** fixture, 2026-10-07: 4.5 vs 1.1 min → [ev](evidence/demo.md)
- **Confidence:** INFERRED — byte-identity proof not run yet
- **Gate:** non-META APK entries byte-identical to a clean build
- **Valid while:** `expo@57` · last_validated: 2026-10-01
- **Source:** DEMO-003

## Not covered / defer to
- Anything else: defer to `expo:expo-overview`.
