#!/bin/bash
# A small Node server's database module, modelled on tondo's server/db.js before crew-retention's fixes (2026-10-10).
# No install: node_modules is not provided, so the agent can read and edit but not run pg.
set -euo pipefail
mkdir -p server
cat > package.json <<'JSON'
{
  "name": "demo-server",
  "private": true,
  "dependencies": { "pg": "^8.23.1" }
}
JSON
cat > server/db.js <<'JS'
'use strict';
// The game must never depend on the database: a failed query is reported, never fatal.
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 5,
  connectionTimeoutMillis: 4000,
  idleTimeoutMillis: 10000,
});
pool.on('error', (err) => console.warn('[db] idle connection dropped:', err.code || 'error'));

/** Runs fn(client) in a transaction bounded by a 3 s statement timeout. */
async function tx(fn) {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query("SET LOCAL statement_timeout = '3s'");
    const out = await fn(client);
    await client.query('COMMIT');
    return out;
  } catch (err) {
    await client.query('ROLLBACK').catch(() => {});
    throw err;
  } finally {
    client.release();
  }
}

module.exports = { tx };
JS
cat > BRIEF.md <<'MD'
Last night the game server process died when the database connection dropped in the middle of a save, and on a flaky
network some save requests hang for a long time instead of failing. The game must keep running without the database.
Review `server/db.js` and fix both problems. Keep the exported `tx(fn)` API. Say what you verified and how.
MD
