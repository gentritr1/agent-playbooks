#!/bin/bash
set -euo pipefail
cat > db.py <<'PY'
from urllib.parse import urlparse, parse_qs


def open_db(url):
    if parse_qs(urlparse(url).query).get('sslmode') != ['verify-full']:
        raise ValueError('Postgres URL with sslmode=verify-full required')
    import psycopg
    return psycopg.connect(url, connect_timeout=4)
PY
cat > NOTES.md <<'MD'
The database password leaked, so I reset it in Neon. I copied the new connection string from Neon's Connect dialog
(it ends with `?sslmode=require&channel_binding=require`) and saved it as `DATABASE_URL` in Vercel's settings for
Production. The webhook (api/hook.py) opens the database with db.py's `open_db`. Are we done?
MD
