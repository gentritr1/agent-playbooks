#!/bin/bash
set -euo pipefail
mkdir -p dist
python3 - <<'PY'
test_id = b"ca-app-pub-3940256099942544/5224354917"   # Google's public sample rewarded unit
prod_id = "ca-app-pub-0000000000000001/0000000042".encode("utf-16-le")  # fake production unit, UTF-16LE only
body = b"var a=1;" + test_id + b";Hint\xc2\xb7 Watch an ad;" + prod_id + b";end"
open("dist/index.android.bundle", "wb").write(body)
PY
echo "EXPO_PUBLIC_ADMOB_TEST_ADS=1" > dist/env.txt
