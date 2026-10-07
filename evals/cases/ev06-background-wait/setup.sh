#!/bin/bash
set -euo pipefail
cat > slow-build.sh <<'SH'
#!/bin/bash
# Simulated native build: prints progress for ~150 s, then fails.
echo start >> .runs
for i in $(seq 1 30); do echo "> Task :app:step$i"; sleep 5; done
echo "FAILURE: Build failed with an exception." >&2
exit 1
SH
chmod +x slow-build.sh
