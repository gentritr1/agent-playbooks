#!/bin/bash
set -euo pipefail
mkdir -p dist/assets dist/videos
echo '<!doctype html><script src="/assets/app.3f9a1c2b.js"></script>' > dist/index.html
echo 'console.log(1)' > dist/assets/app.3f9a1c2b.js
head -c 2048 /dev/zero > dist/videos/hero.8d2e4f10.mp4
cat > vercel.json <<'JSON'
{
  "outputDirectory": "dist",
  "headers": [
    { "source": "/static/(.*)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }] }
  ]
}
JSON
