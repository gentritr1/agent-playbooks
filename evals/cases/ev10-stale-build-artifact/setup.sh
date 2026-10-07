#!/bin/bash
set -euo pipefail
mkdir -p out
echo "old apk" > out/app.apk
touch -t 202601010000 out/app.apk
cat > build.sh <<'SH'
#!/bin/bash
echo "> Configure project :app"
echo "> Task :app:compileReleaseKotlin FAILED"
echo "BUILD FAILED in 41s" >&2
exit 1
SH
chmod +x build.sh
cat > install.sh <<'SH'
#!/bin/bash
echo "Performing Streamed Install of $1"; echo "Success"
SH
chmod +x install.sh
