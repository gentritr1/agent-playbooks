---
name: code-and-doc-lookup
description: Use before searching code for callers or writers, looking up a library API or version range, or trusting an index, language server or docs service.
---

# Code and doc lookup

Where answers come from. Measured on arrows-game 2026-10-07: the same 12 code questions across grep, Graphify, Serena and ast-grep, and 10 version-exact docs questions across Context7, versioned docs and the installed packages. Rejected tools and their traps: `retired/` (PROC-901, LOOK-901..903).

### LOOK-001 · Narrow retrieval: grep the pattern, read the range
- **Rule:** Grep the call or write pattern (`name(`, `setX(KEY`), leave tests out unless the question is about tests, and read only the matching line range.
- **Kind:** heuristic — goal: fewer context bytes for the same answers; override: stronger case evidence, stated in the report; expires: 2027-01-05
- **Evidence:** 12 questions: refined grep 43.3k chars vs 81.1k baseline (median −34 %); ast-grep 45.8k, so the saving is the question, not the tool → [tool-trials](evidence/tool-trials.md)
- **Confidence:** INFERRED — the refined control was written with hindsight; untested on fresh tasks
- **Gate:** searches name a call or write pattern; reads of large files carry a line range
- **Valid while:** grep and Read in Claude Code · last_validated: 2026-10-07
- **Source:** LOOK-001

### LOOK-002 · Library facts come from the installed version
- **Rule:** Take a library's API, defaults and version ranges from the installed package first (types, `compatibility.json`, CHANGELOG), then from the docs URL for that exact version; never from `latest`, `main` or an unversioned docs service alone.
- **Kind:** fact — docs services and unversioned pages answer for another version with the same confidence, and versioned docs drift to the newest patch.
- **Evidence:** Context7 6 of 10 right, 2 for the wrong version (RN 0.86 compileSdk 37 / targetSdk 35, truth 36 / 36; no Reanimated 4.5 data); docs said worklets 0.10–0.11, installed 4.5.1 requires 0.10.x; package files 2k chars vs 53k → [tool-trials](evidence/tool-trials.md)
- **Confidence:** VERIFIED — wrong-version answers observed; the package reads were the ground truth, so their accuracy is by construction
- **Gate:** the report cites the package file or versioned URL and the installed version from `node_modules/<pkg>/package.json`
- **Valid while:** npm projects; Context7 index as seen 2026-10-07 · last_validated: 2026-10-07
- **Source:** LOOK-002

### PROC-003 · An index is checked for staleness and completeness before use
- **Rule:** Stamp any index, graph or summary with the commit and a hash of uncommitted changes and refuse it on mismatch; before trusting an empty or short answer from any index or language server, run one query in the same session whose answer you already know.
- **Kind:** invariant — why: a graph answered an edited tree with old answers, and a live language server returned empty references, both with exit 0 and no warning.
- **Evidence:** Graphify 4 of 4 stale answers labelled `EXTRACTED`; Serena 2 of 12 sessions returned `{}` for every cross-file reference after its 30 s index wait → [graphify](evidence/graphify.md), [tool-trials](evidence/tool-trials.md)
- **Confidence:** VERIFIED
- **Gate:** an invalidation test (edit a file, the old answer is refused) and a known-answer query logged before an empty result is used; on a miss, grep
- **Valid while:** any derived index or language server · last_validated: 2026-10-07
- **Source:** PROC-003

## Gates before you report done
Pattern greps and ranged reads (LOOK-001); library facts cite file or versioned URL plus installed version (LOOK-002); index answers passed the stamp and the known-answer query (PROC-003). A claim in a review still comes from the file or the run, never from the map.

## Not covered / defer to
Expo workflows and versioned Expo docs: `expo:*` skills. Ledger and route experiments for adopting a tool: PROC-002.
