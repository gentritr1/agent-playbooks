---
name: code-and-doc-lookup
description: Before searching code for callers or writers, searching memory notes or lessons, library API or version-range lookups, pointing a note app or tool at memory, or trusting an index, language server or docs service.
---

# Code and doc lookup

Where answers come from. Measured on arrows-game: 12 code questions across grep, Graphify, Serena and ast-grep, and 10 docs questions across Context7, versioned docs and installed packages (2026-10-07); 12 memory questions across grep, an Obsidian MCP server, basic-memory and an index (2026-10-08). Rejected tools: `retired/` (PROC-901, LOOK-901..905).

### LOOK-001 · Narrow retrieval: grep the pattern, read the range
- **Rule:** Grep the call or write pattern (`name(`, `setX(KEY`), leave tests out unless the question is about tests, and read only the matching line range. For a memory or lessons question, `grep -rli` the term, print each matching file with its frontmatter `description:` line, and read only the chosen note.
- **Kind:** heuristic — goal: fewer context bytes for the same answers; override: stronger case evidence, stated in the report; expires: 2027-01-06
- **Evidence:** 12 questions: refined grep 43.3k chars vs 81.1k baseline (total −47 %, median per question +34 % saving); ast-grep 45.8k (total −44 %), so the saving is the question, not the tool; 12 memory questions: refined grep 12 of 12 correct, 45.9k vs 77.8k chars (total −41 %, median per question +40 % saving), ahead of an Obsidian MCP server, basic-memory and an index → [tool-trials](evidence/tool-trials.md), [memory-trials](evidence/memory-trials.md)
- **Confidence:** INFERRED — the code control was written with hindsight; the memory set had one grader and one question set; untested on fresh tasks
- **Gate:** searches name a call or write pattern; reads of large files carry a line range; a memory search lists files with their `description:` before any note is read
- **Valid while:** grep and Read in Claude Code · last_validated: 2026-10-08
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
- **Rule:** Stamp any index, graph or summary with the commit and a hash of uncommitted changes and refuse it on mismatch; before trusting an empty or short answer from any index or language server, run one query in the same session whose answer you already know. A tool that reads from its own database is an index even with a file watcher: edit, then re-read at once.
- **Kind:** invariant — why: a graph answered an edited tree with old answers, and a live language server returned empty references, both with exit 0 and no warning; a note server served old text 0.5 s after an edit.
- **Evidence:** Graphify 4 of 4 stale answers labelled `EXTRACTED`; Serena 2 of 12 sessions returned `{}` for every cross-file reference after its 30 s index wait; basic-memory returned the old note at +0.5 s, fresh at +20 s → [graphify](evidence/graphify.md), [tool-trials](evidence/tool-trials.md), [memory-trials](evidence/memory-trials.md)
- **Confidence:** VERIFIED
- **Gate:** an invalidation test (edit a file, the old answer is refused) and a known-answer query logged before an empty result is used; for a store with its own database, an edit followed by an immediate re-read shows the new text; on a miss, grep
- **Valid while:** any derived index, note store or language server · last_validated: 2026-10-08
- **Source:** PROC-003

### LOOK-003 · Writing apps and tools never touch live memory or repo docs
- **Rule:** Never point an app or tool that can write (Obsidian, basic-memory, an MCP note server) at `~/.claude/projects/*/memory` or a repo `docs/` folder; give it a one-way read-only copy and prove byte-identity by sha256 before and after.
- **Kind:** invariant — why: the writes are silent, and agents load memory notes in every session.
- **Evidence:** basic-memory's first sync rewrote 528 of 536 notes; an Obsidian link-update dialog ("Just once") rewrote 3 notes including `MEMORY.md`; a read-only copy kept 492 of 492 byte-identical → [memory-trials](evidence/memory-trials.md)
- **Confidence:** VERIFIED — sha256 before and after in the named runs (Obsidian 1.4.5, basic-memory 0.23.2, MCPVault 0.16.0)
- **Gate:** the tool's root is a copy (read-only on disk), and `shasum -a 256` over the live notes before and after the session is identical
- **Valid while:** any app or tool that can write notes; `ctx:any` · last_validated: 2026-10-08
- **Source:** LOOK-003

## Gates before you report done
Pattern greps and ranged reads (LOOK-001); library facts cite file or versioned URL plus installed version (LOOK-002); index answers passed the stamp and the known-answer query (PROC-003); live memory hashes unchanged (LOOK-003). A claim in a review still comes from the file or the run, never from the map.

## Not covered / defer to
Expo workflows and versioned Expo docs: `expo:*` skills. Ledger and route experiments for adopting a tool: PROC-002.
