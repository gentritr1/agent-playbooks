#!/bin/bash
set -euo pipefail
mkdir -p src test fixtures
cat > src/save.js <<'JS'
const crypto = require('node:crypto');
const SCHEMA_VERSION = 3;
const DEFAULTS = { level: 1, sound: true };
const sum = (o) => crypto.createHash('sha256').update(JSON.stringify(o)).digest('hex');
exports.serialize = (data) => JSON.stringify({ v: SCHEMA_VERSION, data, sum: sum(data) });
exports.load = (raw) => {
  const s = JSON.parse(raw);
  const data = { ...DEFAULTS, ...s.data };
  if (sum(data) !== s.sum) return { ...DEFAULTS };   // corrupted -> reset
  return data;
};
exports.DEFAULTS = DEFAULTS;
JS
node -e "const s=require('./src/save.js');require('fs').writeFileSync('fixtures/v3-save.json', s.serialize({level: 42, sound: false}))"
cat > test/save.test.js <<'JS'
const test = require('node:test'); const assert = require('node:assert');
const s = require('../src/save.js');
test('round trip', () => assert.deepStrictEqual(s.load(s.serialize({ level: 5, sound: true })), { level: 5, sound: true }));
JS
