# Independent oracles: where they re-derive, and where they only agree

**Source:** lomn-web `docs/knowledge/audits/2026-10-07-m1a3-osi-textures-parser-security.md` (defect 3, Lessons); lomn-web `docs/knowledge/web-porting-playbook.md` §8; lomn-web `.superpowers/sdd/2026-10-07-lomn-web-m1a3/progress.md` (Task 3 and Task 5 reviews, Task 8A); lomn-web `.superpowers/sdd/2026-10-07-lomn-web-m1a4/progress.md` (controller decomp check) and `task-4-review.md` (I-1, mutation tables); lomn-web project memory `lomn-toolchain-gotchas.md` (2026-10-07 entries).

Project: LOMN web port, a C++17 port of a 2001 PC game to native + wasm32 WebGPU, checked against Python oracles written separately from the C++. All three firings are from 2026-10-07.

## Firing 1: a transcribed constant (M1a-3 Task 5)
- The reference implementation and its "independent" A9 oracle both used two FourCC sort ids in big-endian order; the binary stores them so that they read little-endian. Result: 9/123 real areas mis-ordered draws.
- "no test sees it (oracle shares constants, synthetic scene lacks" those ids). The builder had noted the ids "never match"; a reviewer accepted it.
- Found by sweeping the oracle over all 123 areas (96 agree) and reading the exe bytes. Fixed in Task 8A (ids from the exe bytes; `make a9-sweep` 123/123).

## Firing 2: a mismatch explained away (M1a-3 Task 3)
- 32-bit push literals were decoded unsigned: a `cond ? int32_t : uint32_t` ternary decays to `uint32_t`, so 65 real colour arguments differed from Python by 2³², and folds were wrong (INT_MIN / −1 gave 0.5).
- "The implementer and the controller had both accepted this mismatch as "the same 32-bit pattern"." The unit test cast through `uint32_t`, so it hid the bug.
- Exposed only by comparing all 8,406 real class.method pairs (7,263 calls), now ctest `osi_all_methods`, 0 mismatches.

## Firing 3: a shared semantic reading (M1a-4 Task 4)
- The oracle and the C++ shim modelled one script-callable native the same way: a scale on true, a no-op on false. The controller's decomp read (executed) shows an overwrite on both branches.
- `make a9-sweep` was 123/123 equal; 29 of the 123 areas' last call takes the "no-op" branch. The in-game effect is UNVERIFIED (call order not yet resolved); the review estimates a 17-20 % brightness difference on those areas if the lights are active.
- Reviewer's detection rule: "for every "INFERRED never happens" in an oracle, grep the real data for that case before accepting it." Memory's brief update: oracle work needs a decomp citation per modelled native and a count of real call sites per branch.

## What re-derivation buys (M1a-4 Task 4 review, executed)
- Every constant the oracle cites was re-read from the exe's `.rdata` with the reviewer's own PE section mapper and matched.
- Of 9 C++ shim mutations, 2 (the intensity knee 0.9 -> 1.0 and swapped `atan2` arguments) passed the synthetic-only oracle and were caught only by the real-data oracle, which needs the game files.
- The camera is the one honest exception: a transliteration of the C++ (the spec defines no camera), disclosed as such.
