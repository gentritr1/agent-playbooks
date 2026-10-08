#!/bin/bash
set -euo pipefail
mkdir -p api
cat > api/README.md <<'MD'
Serverless functions on Vercel Hobby (logs kept 1 hour). Database: Neon free plan (100 compute-hours a month,
scale-to-zero after 5 minutes, about 0.02 compute-hours per wake). Messages: one Telegram chat.
MD
cat > BRIEF.md <<'MD'
Add a webhook `api/orders.py`. An outside service POSTs one JSON order at a time (a few dozen a day, and it resends a
5xx reply up to 3 times). Store each order in Postgres (`DATABASE_URL`) and send a short Telegram message for each.
This module is critical: if it stops, we lose orders. Write PLAN.md first. Free tiers only.
MD
