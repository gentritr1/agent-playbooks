# Graphify trial: a cache without a freshness check

**Source:** arrows-game `docs/process/graphify-trial-2026-10-07.md` (route experiment, load 14–47, worktree at `ace959b`); `~/.claude/CLAUDE.md` §10 "Project memory and caches never go stale silently".

| Measure | Result |
|---|---|
| Accuracy on 12 real questions | 3 correct, 9 partial, 0 wrong; one partial was confidently misleading (`EXTRACTED`, pointed at an interface instead of the write site) |
| Cost to a correct answer vs grep+read | median −7.5 % (the graph cost more); range −983 % to +95 % |
| Staleness without rebuild | 4 of 4 edits returned the old answer, exit 0, labelled `EXTRACTED`, no warning |
| Built-in freshness check on query | none |
| Rebuild | cold median 21 s, update median 23 s; "incremental" re-extracted 351 of 650 files |
| Stamp guard (commit + diff hash + untracked blobs) | 0.3 s, refused stale graphs |

Verdict REJECT as project memory. Reopen only with a ledger showing "who calls X" questions dominate re-read cost and a graph that indexes literal values. A cheaper alternative proposed: a generated lessons index with a hash test.
