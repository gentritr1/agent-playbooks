# Headless WebGPU in Playwright: a blank canvas that reports "drawn"

**Source:** lomn-web `docs/knowledge/web-porting-playbook.md` §5; lomn-web `docs/knowledge/measurements.md` (Runtime: browser triangle); lomn-web `web/tests/smoke.mjs` (header comment and checks); lomn-web `web/package.json` and `web/node_modules/playwright-core/browsers.json`; lomn-web project memory `lomn-toolchain-gotchas.md`.

Measured 2026-10-07 on a MacBook M1 Pro, macOS 26.5.2, Playwright 1.63.0 (its Chromium build is 153.0.8010.12).

| Playwright config | Adapter | Canvas screenshot |
|---|---|---|
| default headless shell | none | n/a |
| headless shell + `--enable-unsafe-webgpu` | SwiftShader | **blank white while page state says "drawn"** (false positive) |
| `channel:'chromium'` + `--enable-unsafe-webgpu` | Apple Metal | correct (`ff8000` centre, `000040` corner) |

- The smoke test launches `channel: 'chromium'` with `--enable-unsafe-webgpu`, prints the adapter (`vendor/architecture`), and fails unless the centre pixel is the orange triangle and the corner the clear colour (each channel within 2 levels). It also fails on `[webgpu]` console errors, page exceptions and requests outside the built site.
- Frame reconciliation: "dt samples must equal frames − 1"; measured 120 frames, 119 dt samples, p50 16.70 ms (vsync).
- "Every runner needs a negative test. The smoke test fails in 1.5 s against an empty site."
- Memory: "Always assert pixels."
