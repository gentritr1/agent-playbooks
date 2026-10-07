# Delegation, worktrees, git bookkeeping and outward steps

**Source:** `~/.claude/CLAUDE.md` §4, §5, §6; arrows-game memory `codex-delegation-setup.md` (2026-09-19), `reward-path-2026-10-04.md`, `owner-rulings-next-level-2026-09-16.md` (push note 2026-10-01), `shared-host-contention.md` (2026-09-27 cleanup); secret-dictator memory `delegation-review-loop.md` (2026-08-08); geoguesser-app memory `agent-worktree-isolation-cuts-from-main.md` (2026-10-02), `worktree-remove-deletes-evidence.md` (2026-10-04), `gate-commits-on-the-exit-code.md` (2026-10-02/04); tondo, secret-dictator-v2, lucky-shelf, apollonia-events, pizzuno memories (shared-checkout collisions); wordle memory `dev-environment-gotchas.md`; arrows-game `docs/engineering-lessons.md` (W1-11 jest scoping).

## Briefs and reviews
- Codex does not read CLAUDE.md, so verification rules are restated in a shared brief file; without network and add-dir flags Gradle and adb fail in its sandbox.
- Reward path A and collection book B (2026-10-04): told to audit each plan task against live code, Codex stopped 6 times per plan on real conflicts; each was fixed by a plan/spec commit rather than in chat.
- secret-dictator (2026-08-08): delegates ran their own verification; the reviewer re-ran the scenarios independently and in every one of four rounds caught something the report missed. Delegate transcripts expire, so briefs must stand alone.

## Worktrees
- geoguesser-app 2026-10-02: `isolation: "worktree"` branched from `main`, not the feature branch; same pattern in gold-pdf-bot (stale origin/main) and pizzuno (3 times in one cycle). Fix in all three: create the worktree yourself and have the dispatch verify HEAD.
- Two implementers in one checkout broke work in tondo, secret-dictator-v2, lucky-shelf, apollonia-events and pizzuno.
- geoguesser-app 2026-10-04: `git worktree remove --force` after each merge deleted every unit's gitignored evidence directory.
- Test runners crossed trees: `npx jest <path>` also ran other sessions' worktree copies (arrows-game; scope with `"$PWD/(src|scripts)/"`); bare `node --test` discovered other agents' worktrees (wordle).

## Bookkeeping after state changes
- geoguesser-app 2026-10-02: a 904/905 run was committed because nothing tied the commit to the test result.
- geoguesser-app 2026-10-04: a failed `merge --ff-only` chained with `;` was followed by a "merged" ledger line, a pushed handoff row, the reviewed worktree's removal and a new worktree from a tree without the unit; the printed count, 2219 not 2275, was the unread tell.

## Outward and irreversible steps
- arrows-game 2026-10-01: a push of 78 commits went ahead on the owner's "push these" after checking for artifacts and secrets; each later push still needs its own yes.
- arrows-game 2026-09-27: an emergency `find artifacts -name "*.mp4" -mtime +0 ! -path "*/owner/*" -delete` also deleted 8 owner-acceptance videos named `owner-*.mp4` outside an `owner/` folder. Rule: build the keep-list from the reports first.
