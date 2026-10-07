---
name: binary-and-wasm-porting
description: Before untrusted-format parsers, caps or fuzzing, oracles or cross-checks, wasm32 builds, native-vs-wasm determinism, or headless WebGPU tests.
---

# Binary and wasm porting

From the LOMN web port (2026-10-07): C++17, native arm64 and wasm32 WebGPU, players' own game files, Python oracles.

### PORT-001 · An oracle proves correctness only where it re-derives
- **Rule:** Derive an oracle's constants and modelled behaviour from the binary, docs or spec, never the implementation; agreement proves consistency only; a mismatch is a defect until traced through every use.
- **Kind:** invariant — why: whatever the oracle transcribes fails together with the implementation.
- **Evidence:** FourCC ids byte-swapped on both sides (9/123 areas); a `cond ? int32_t : uint32_t` decay accepted as "the same 32-bit pattern" (65 real arguments off by 2³²); a native modelled identically wrong while the sweep was 123/123 (29 areas) → [oracles](evidence/oracles.md)
- **Confidence:** VERIFIED — each firing reproduced by a reviewer; the third one's in-game effect is UNVERIFIED
- **Gate:** each oracle constant and branch cites binary, docs or spec; a full-corpus run per milestone; the review counts real call sites per branch and compares all entries
- **Valid while:** any oracle or cross-implementation check · last_validated: 2026-10-07
- **Source:** PORT-001

### PORT-002 · Parser caps come from measured maxima; a rejection leaves no partial state
- **Rule:** Cap every attacker-controlled count and accumulation at ≥ 16× the measured real maximum (or a format bound), measure worst cases on wasm32 too, and commit parsed state only on success.
- **Kind:** invariant — why: a crafted file of a few hundred KB aborts the wasm32 page (32-bit `size_t`, no exceptions, 2 GB heap) while real files pass; a cap below real data costs fidelity.
- **Evidence:** a 672 KB BLK aborts wasm32 at 2 GB; a 64 MiB SLB table reached 1,273 MB on wasm32 (per-record name copies); caps e.g. 5,489 → 131,072; a failed open left stale `find()` hits → [parser-caps](evidence/parser-caps.md)
- **Confidence:** VERIFIED
- **Gate:** each cap names its measured max; cap ÷ max ≥ 16 or a format bound; oracles green after; a crafted probe per count, native and wasm32, ends in a named error within a stated bound; a test shows a failed parse leaves no partial state
- **Valid while:** C++17, native arm64 and wasm32 (Emscripten, 2 GB max memory); maxima from one game build · last_validated: 2026-10-07
- **Source:** PORT-002

### PORT-003 · A fuzz zero counts only beside proof of depth and teeth
- **Rule:** Report a fuzz zero only with per-input time and heap invariants, per-format deep-reach counts, a re-introduced known defect it reports, and crafted probes beside it.
- **Kind:** invariant — why: fuzzers reported zero while amplification defects sat in the code.
- **Evidence:** ≈ 120 M native + ≈ 1.7 M wasm32 inputs, 0 findings, while the audit's 7 findings were "found only by crafted inputs"; a per-input heap invariant then caught a TGA growth of 67,119,136 bytes over the limit → [parser-caps](evidence/parser-caps.md)
- **Confidence:** VERIFIED — zeros beside defects, and the heap invariant's finding; the ≥ 5 % deep-reach floor and re-introduced defects are INFERRED (briefed, not yet measured)
- **Gate:** per format: inputs, accepted, deep reach (≥ 5 % in the smoke test), findings; a re-introduced past defect per format family is reported; zeros beside these controls (TEST-002)
- **Valid while:** ASan+UBSan `-fno-sanitize-recover`, native and wasm32 under Node · last_validated: 2026-10-07
- **Source:** PORT-003

### PORT-004 · Headless WebGPU can paint a blank canvas and still say "drawn"
- **Rule:** Run headless WebGPU tests with `channel: 'chromium'` and `--enable-unsafe-webgpu`, and assert the adapter and canvas pixels, never a page state flag alone.
- **Kind:** fact — the default headless shell has no adapter; with the flag it gets SwiftShader, whose screenshot is blank white while page state says "drawn"; the Chromium channel gets Metal and correct pixels.
- **Evidence:** Metal: centre `ff8000`, corner `000040`; 120 frames, 119 dt samples; fails in 1.5 s against an empty site → [headless-webgpu](evidence/headless-webgpu.md)
- **Confidence:** VERIFIED
- **Gate:** the test prints the adapter and fails unless known pixels match (≤ 2 levels); dt samples = frames − 1; a run against an empty site fails
- **Valid while:** `playwright@1.63` `ctx:web` · Chromium 153.0.8010.12, macOS 26.5.2, Apple M1 Pro / Metal · last_validated: 2026-10-07
- **Source:** PORT-004

### PORT-005 · Native and wasm32 deterministic logs are byte-identical
- **Rule:** Compile the shared core with `-ffp-contract=off` as a PUBLIC option, print non-finite floats yourself, and `cmp` native and wasm32 traces and logs in the test target.
- **Kind:** invariant — why: tests run native while wasm32 ships; a print or FMA difference hides or fakes divergence.
- **Evidence:** trace byte-identical over 600 frames; `%.6g` printed NaN as `nan` on macOS, `-nan` under Emscripten/musl: RED on wasm32 until spelled explicitly → [wasm-determinism](evidence/wasm-determinism.md)
- **Confidence:** VERIFIED — identity and the NaN split measured; the FMA reason is the build file's, not measured
- **Gate:** the test target `cmp`s native and wasm32 logs; a ±NaN, ±inf, −0 case prints alike on both; the flag is PUBLIC on the core
- **Valid while:** `ctx:wasm` · Apple clang arm64 vs Emscripten 6.0.11 wasm32 under Node · last_validated: 2026-10-07
- **Source:** PORT-005

## Gates before you report done
Oracle citations and full sweep (001); measured caps, wasm32 probes, no partial state (002); fuzz controls (003); pixels asserted (004); native == wasm32 `cmp` (005).

## Not covered / defer to
Red-first tests, mutants and positive controls in general: `testing-gates` (TEST-001, TEST-002). Pixel tolerances for GPU renders: `ui-motion-quality`. Browser checks of your own pages: `browser-automation`.
