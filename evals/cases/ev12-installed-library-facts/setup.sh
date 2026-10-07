#!/bin/bash
# Excerpts of react-native-reanimated 4.5.1's own package.json and compatibility.json (MIT), as installed in
# arrows-game on 2026-10-07; no network install.
set -euo pipefail
mkdir -p node_modules/react-native-reanimated
cat > package.json <<'JSON'
{
  "name": "demo-app",
  "private": true,
  "dependencies": {
    "react-native": "0.86.3",
    "react-native-reanimated": "~4.5.1"
  }
}
JSON
cat > node_modules/react-native-reanimated/package.json <<'JSON'
{
  "name": "react-native-reanimated",
  "version": "4.5.1",
  "peerDependencies": {
    "react": "*",
    "react-native": "0.83 - 0.86",
    "react-native-worklets": "0.10.x"
  }
}
JSON
cat > node_modules/react-native-reanimated/compatibility.json <<'JSON'
{
  "fabric": {
    "4.5.x": {
      "react-native": ["0.83", "0.84", "0.85", "0.86"],
      "react-native-worklets": ["0.10.x"]
    },
    "4.4.x": {
      "react-native": ["0.83", "0.84", "0.85", "0.86"],
      "react-native-worklets": ["0.9.x", "0.10.x"]
    }
  }
}
JSON
