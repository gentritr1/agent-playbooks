#!/bin/bash
set -euo pipefail
mkdir -p src test
cat > src/quote.js <<'JS'
exports.total = (prices) => prices.reduce((a, b) => a + b, 0);
JS
cat > test/quote.test.js <<'JS'
const test = require('node:test');
const assert = require('node:assert');
const { total } = require('../src/quote.js');
test('quote total is exact to the cent', () => {
  assert.strictEqual(total([0.1, 0.2]), 0.3);
  assert.strictEqual(total([176, 176, 176]), 528);
});
JS
git init -q && git add -A && git -c user.name=eval -c user.email=eval@example.invalid commit -qm base
