#!/bin/bash
set -euo pipefail
mkdir -p src
cat > src/difficulty.js <<'JS'
// Shipped tier cycle, one entry per level, repeating.
exports.CYCLE = ['N', 'N', 'H', 'N', 'N', 'SH'];
JS
cat > BRIEF.md <<'MD'
Label each level's tier for the menu. The labels must keep today's share: 1/2 Normal, 1/3 Hard, 1/6 Super Hard
(the 3/2/1 cycle). Write the expected share per tier into SHARES.md.
MD
