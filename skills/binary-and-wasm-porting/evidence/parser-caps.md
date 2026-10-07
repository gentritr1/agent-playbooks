# Untrusted-format parsers: measured caps, wasm32 amplification, partial state, fuzz teeth

**Source:** lomn-web `docs/knowledge/audits/2026-10-07-m1a1-parser-security.md`; lomn-web `docs/knowledge/audits/2026-10-07-m1a3-osi-textures-parser-security.md`; lomn-web `docs/knowledge/measurements.md` (M1a-3 OSI maxima and fuzz); lomn-web `docs/knowledge/web-porting-playbook.md` §8; lomn-web `.superpowers/sdd/2026-10-07-lomn-web-m1a3/progress.md` (Task 3 review, Ruling R3); lomn-web `.superpowers/sdd/2026-10-07-lomn-web-m1a4/task-1-brief.md`; lomn-web commits `74a5a69` and `2856ce9` (messages); lomn-web project memory `lomn-toolchain-gotchas.md`.

Threat model (both audits): players bring their own game files, so every file is untrusted. The browser build is wasm32: "`size_t` is 32-bit, exceptions are disabled (an uncaught error aborts), and the heap is capped at 2 GB" (`-sMAXIMUM_MEMORY=2GB`).

## Amplification found by crafted inputs (before → after)
| Audit | Defect | Crafted input | Before | After |
|---|---|---|---|---|
| M1a-1 | BLK unterminated names copied to the next NUL (quadratic) | 12,000 entries, a 672 KB file | wasm32 aborts at 2 GB; natively ≈ 4 GB | instant error, 3.5 MB |
| M1a-1 | `.x` material reference re-decoded per reference | 40,000 references, 880 KB | 4.8 s native | 0.005 s |
| M1a-1 | `.x` texture name copied into every material reference | 35,000 refs × 70 KB name, 460 KB | wasm32 aborts | instant error |
| M1a-3 | OSI `find_calls` accumulated with no cap | a 600 KB crafted script | 473 MB natively | named error |
| M1a-3 | SLB texture table uncapped, each record copied a 255-character name | a 64 MiB table | 1,273 MB on wasm32; the probe accepted it at +375 MB | rejected at +10.7 MB native, +12.9 MB wasm32 |
| M1a-3 | OSI classes/methods uncapped, each method copied its symbol name | an 8 MiB file | 429 MB on wasm32 | rejected; names stored as symbol indices |
| M1a-3 | applying the texture table was O(subsets × records) | a 62 MB table | 11.9 s hang | O(subsets log records) |

"Why the earlier checks missed them: every real file is benign", so oracles, the whole-install ASan run and mutations could not see these.

## Caps from measured maxima (M1a-3: "≥16× headroom unless the format bounds it")
| Quantity | Measured real max | Cap | Headroom |
|---|---|---|---|
| BLK unterminated-name run past 40 bytes | 2 bytes | 512 bytes | 256× |
| `.x` objects per file | 5,489 | 131,072 | ≈ 24× |
| `.x` texture-name length | 36 bytes | 576 bytes | 16× |
| OSI file size | 486,274 B | 8 MiB | 17× |
| OSI instructions per subroutine | 1,707 | 32,768 | 19× |
| OSI classes / methods | 395 / 8,406 | 8,192 / 262,144 | 20.7× / 31× |
| SLB texture-table records | 15 (over 18 real tables) | 1,024 | 68× |
| SLB texture-name length | 35 | 63 | the exe's own fixed-string bound |

- Ruling R3 (M1a-3): the brief's method cap of 131,072 "broke the ≥16× headroom rule", so 2^18 was accepted.
- After every cap change the oracles were re-run: "still 39/39". Caveat: one game build was measured (Beta 1.5.0).
- Remaining bounded worst case: a 64 MiB `.x` entry reaches ≈ 580 MB of wasm32 heap (≈ 9× the file size), so a loose `.x` of roughly 220 MB or more would hit the 2 GB limit (open item).

## No partial state
- M1a-1: a failed BLK `open` left partial entries visible ("Stale `find()` hits"); a failed `enter_area` kept the previous area open. Both fixed to empty state.
- M1a-3: "Hitting a cap is an error and leaves **no partial state**"; a texture table is built locally and assigned only on success.
- M1a-4 (`74a5a69`): the new fuzz driver found on its first run that a failed LZSS decode, BLK read or SLB parse left partial output; unit tests fail on the old code (9 assertions).

## Fuzz zeros beside real defects
- M1a-1 fuzzing totals, all rounds: ≈ 120 M native and ≈ 1.7 M wasm32 inputs, 0 sanitizer findings, 0 invariant failures. The audit's 7 findings (5 amplification, 2 partial-state) "were found only by crafted inputs".
- M1a-3 Task 3 review: OSI fuzz 34k native + 27.6k wasm32 and texture-table fuzz 7.1M + 58k, "0 findings", in the same review that found the uncapped table (64 MiB → 1,273 MB on wasm32) with a crafted probe.
- M1a-4 (`2856ce9`): the format fuzzer, with real seeds and a 64 MiB per-input heap invariant, found a TGA decoder that allocated the pixel buffer before checking the data length: "a heap growth of 67,119,136 bytes over the 64 MiB per-input limit" (an 8,949-byte real TGA with its header inflated to 4096x4096x32).
- M1a-4 Task 1 brief (results not yet in `measurements.md`): the smoke test "asserts 0 findings, and that deep reach is at least 5 % of inputs per format"; "Proof the fuzzer bites": re-introduce one known past defect per format family in a scratch copy, and the fuzzer must report each within its normal run.
- M1a-3 mutation bite check: 40 of 42 caught; the NaN vertex-colour mutation is invisible to value tests and caught only under UBSan (`nan is outside the range of representable values`).
