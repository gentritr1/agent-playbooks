# Memory-tool trial: refined grep, Obsidian MCP, basic-memory, in-house index (2026-10-08)

**Source:** arrows-game `docs/process/obsidian-memory-trial-2026-10-08.md` (route experiment; throwaway copies of 536 notes: 492 agent memory notes from 45 projects, the arrows-game lessons file, 43 playbook files; sandboxed, no outbound network except one model download, nothing registered in any Claude config; shared host, load average 9-121, one grader, 12 memory questions with ground truth read from the notes). Compare each row with its own baseline, not with the 2026-10-07 code questions in [tool-trials](tool-trials.md).

## 12 memory questions
| Route | Correct / partial / wrong | Chars, 12 Q (total vs baseline 77,768) | Median per-question saving | Fixed cost per session |
|---|---|---|---|---|
| Baseline `grep -rn` + read | 12 / 0 / 0 | 77,768 | 0 | 0 |
| **Refined grep:** `grep -rli`, one line per file with its `description:`, then read one note | 12 / 0 / 0 | 45,889 (**-41.0 %**) | **+40.1 %** (-4 to +65) | 0 |
| In-house description + backlink index (153 lines) | 11 / 0 / 0, one grep fallback | 48,832 (-37.2 %) | +11.2 % | 0 |
| MCPVault 0.16.0 (Obsidian MCP), full answers | 9 / 3 / 0 | 65,810 (-15.4 %) | -7.0 % | 10,867 chars (18 tools) |
| basic-memory 0.23.2, full answers | 10 / 2 / 0 | 78,729 (+1.2 %) | -30.9 % | 36,730 chars (21 tools + instructions + `recent_activity`) |

- **The saving is the output shape:** one line per file with its curated `description` is what both the index and the refined grep print; the grep needs no index and cannot go stale. The first queries were written from the question's words, but one person wrote the questions and graded them, so LOOK-001 stays INFERRED.
- 19 of 536 notes have no `description`; the grep still matches bodies, so a note without one is found but ranked blind.
- No route gave a confidently wrong answer. The closest was Q1 through a memory note that quotes the Graphify median per question with the sign flipped in words and omits the total (+11.5 %): a memory-quality finding, fixed in the note, not a tool finding.

## Writes (LOOK-003)
| Event | Result |
|---|---|
| basic-memory, default first sync on a copy | **528 of 536 notes rewritten** (added `permalink`, re-wrapped YAML, changed the `modified:` timestamp format, dropped the final newline) |
| basic-memory, configuration that leaves notes untouched | notes byte-identical, but its graph returned 0 relations and `read_note("SKILL")` failed (45 notes share the name `MEMORY.md`, 11 `SKILL.md`) |
| Obsidian 1.4.5 opened on a writable copy, defaults, indexed ~60 s | 536 of 536 notes byte-identical (sha256); only `.obsidian/` (6 files) written |
| Obsidian, rename of a note with 3 backlinks, dialog answered "Just once" | **3 other notes rewritten, including `MEMORY.md`**, the index Claude Code loads into every session; "Always update" would also flip the setting for good |
| Obsidian, no-op frontmatter write | the note was rewritten (YAML re-serialised) |
| Same three writes on a read-only one-way copy | `EACCES` on each; **492 of 492 notes byte-identical** |
| MCPVault tool list | write, patch, move and delete tools pointed at the memory |

Guard used: sha256 of every note before and after, sorted; a read-only copy refreshed by `rsync --delete` from the live folders.

## Staleness (PROC-003)
| Route, edit then re-ask, no re-index | Changed fact | New note | Deleted link |
|---|---|---|---|
| grep, MCPVault (no index) | fresh | fresh | fresh |
| In-house index, check off | stale | stale | stale |
| In-house index, content fingerprint on every query | fresh (rebuilt or refused) | fresh | fresh |
| basic-memory, +0.5 s after the edit | **stale: `read_note` returned the old body and old description** (it serves its database copy) | fresh | stale |
| basic-memory, +20 s, and in a new session | fresh | fresh | fresh |

basic-memory runs a file watcher and still served the old text at +0.5 s, so a watcher does not make a store a view of the files. Its first index took 979 s (16.3 min) and its CLI `reindex` re-embedded all 538 notes after 3 edits.

## Not trialled
Hindsight (`vectorize-io/hindsight`): ingestion needs an LLM over every note. No local model is installed; the cloud path would send about 0.7 M tokens (536 notes, ~2.7 MB, which include ad-network keys) to a provider; its Claude Code plugin hooks `UserPromptSubmit` (every prompt) and `Stop`. Owner decision, not a rejection; see the README.
