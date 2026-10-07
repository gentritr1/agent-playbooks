# Code-navigation and docs tool trials (2026-10-07)

**Source:** arrows-game `docs/process/agent-memory-tools-2026-10-07.md` (route experiment; throwaway worktree pinned to `ace959b`; sandboxed, no network except Serena's first-run language-server download; host load 21–70). Same 12 questions and ground truth as the Graphify trial ([graphify](graphify.md)), so the rows compare directly. Chars are what an agent reads to reach the full truth; tokens ≈ chars / 4.

## Code questions (12; ground truth read from the code at `ace959b`)
| Route | Correct / partial / wrong / n/a | Chars, 12 Q (total change) | Median per-question saving vs baseline |
|---|---|---|---|
| Baseline grep + whole reads | (reference) | 81,066 | 0 |
| **Refined grep** (call or write pattern, tests excluded, line ranges) | (reference answers) | 43,254 (total −46.6 %) | +34.1 % (−4 to +92) |
| ast-grep 0.45.3, realistic | 8 / 2 / 0 / 2 | 45,786 (total −43.5 %) | +39.2 % (−16 to +92) |
| Serena 1.7.0 (LSP over MCP), realistic | 6 / 4 (2 misleading) / 0 / 2 | 76,502 + 32,472 per session | 0.0 % (−80 to +70) |
| Graphify | 3 / 9 / 0 / 0 | 90,393 (total +11.5 %) | −7.5 % |

- **The saving is the question, not the tool:** ast-grep and refined grep save about the same, and both used hindsight (they named `PETALS`, `HALLOWEEN_BOARD`, `internal fun`). Hence LOOK-001 is INFERRED until the eval harness measures it on fresh tasks.
- **ast-grep traps:** `-l ts` silently skips `.tsx` (Q7: `ads.tsx`); an identifier pattern skips property keys (Q3: 0 test files); 3 of ~25 patterns matched nothing, which looks like "no results".
- **Serena traps:**
  - Before its first cross-file reference query it waits at most 30 s for tsserver indexing; if indexing is unfinished it logs `complete=False` to the server's stderr only and never waits again. In 2 of 12 sessions every cross-file reference query then returned partial or empty JSON for the whole session (`feedbackSoundOn`: `{}`, truth 3 files; `displayTier`: `{}`, truth 4). Not simply load: one failure at load 30–41, successes at 44–53.
  - References through a structural interface are missed even in complete sessions (Q5: the production caller of `setGenSwitchLevel`, 3 of 3 sessions).
  - Line numbers are 0-based (`> 933:` is file line 934).
  - Its `claude-code` context prompt marks Read and Edit "FORBIDDEN", and its recommended hook denies the third consecutive Grep/Read: both push the agent away from the read that would catch the gaps above.
  - It pings a usage endpoint on every start unless disabled; it writes a 26 MB cache into the repo.
- **Freshness:** Serena and ast-grep answered 4 of 4 edits correctly without a rebuild (Graphify: 4 of 4 stale). A live tool can be fresh and still silently incomplete, which PROC-003's invalidation test does not catch; a known-answer query does.

## Docs questions (10, version-exact; installed: expo 57.0.18, react-native 0.86.3, reanimated 4.5.1, react-native-google-mobile-ads 17.1.0, expo-audio 57.0.4, expo-store-review 57.0.3)
| Route | Result | Chars |
|---|---|---|
| Context7 (`context7.com` API, as `ctx7` 0.5.13 calls it) | 6 correct, 1 partial, 3 wrong after follow-ups; 2 wrong-version | 53,023 (34,718 first calls) |
| WebFetch of the versioned docs page | 7 correct, 1 partial (version drift), 2 no answer, 0 wrong-version | a few hundred per page (summary) |
| Installed package (`node_modules` types, `compatibility.json`, `package.json`) | 8 correct, 1 partial (D1–D9) | 2,011 |

- **Wrong-version answers:** D2, Reanimated 4.5's worklets range: Context7 has no 4.5 data (its index lists 3.17.4, 3.19, 4.1.5) and cited 4.0/4.1. D9, RN 0.86 SDK levels: Context7 answered compileSdk 37 / targetSdk 35 from another version's gradle file (truth 36 / 36). Context7's `/expo/expo` lists `sdk-54`..`sdk-56` only.
- **Docs drift to the newest patch:** the versioned docs said worklets "0.10.x and 0.11.x"; installed 4.5.1 peer-requires `0.10.x`.
- **Unversioned service on a non-npm question:** D10, Vercel's CDN-only header: Context7 wrong twice; the official page was right.
- **Caveat:** the installed-package column is circular (ground truth was read from it); it is listed for cost.
