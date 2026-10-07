#!/bin/bash
set -euo pipefail
cat > analyze.sh <<'SH'
#!/bin/bash
# Simulated analysis over a large data set: prints progress for ~200 s, then the total. Succeeds.
echo start >> .runs
for i in $(seq 1 40); do echo "batch $i/40"; sleep 5; done
echo "TOTAL 48213"
SH
chmod +x analyze.sh
