---
name: handoff-beads
description: >-
  Session handoff whose artifact is the bead graph, not a markdown brief.
  Mine the conversation, create only the work that is not already in the
  graph, hang those beads in the right places, then run /beads:validate.
  Use when the next agent should pick up from `bd ready` instead of a
  handoff doc. Invoke as /handoff-beads [project].
---

# /handoff-beads

Handoff by updating the bead graph. Mine this session the way a prose
handoff would, then persist only unrecorded work as beads, placed with
real parents and causal edges. Do not write a handoff markdown file.

If `/handoff` is installed you may reuse its mining; you still must not
write its file. The steps below stand alone.

Execute without asking for confirmation, unless several unrelated projects
are in play.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates).

Parse:

1. **Non-flag text** — the project or topic to hand off.
2. **Empty** — the session's primary project.
3. **Several unrelated projects** — ask which one. One project per run.

## Procedure

### 1. Mine the conversation

Before any command, extract from THIS session:

- **The project** — what we are building, in one or two sentences, and why.
- **Pivot points** — approaches tried and abandoned (and why they failed),
  scope cuts, renames, decisions the user locked in.
- **Open questions** — deferred, "later", or left ambiguous.
- **Landmines** — env quirks, flaky specs, wedge-prone commands, ordering
  constraints that already cost time.
- **Next steps** — concrete remaining work, including half-done stopping
  points (file, command, or PR).
- **Referenced sources** — `docs/future/*.md`, memory files, bead ids,
  external docs this session used or created.

Pivots and landmines beat inventory. A fresh agent can re-derive file
lists; it cannot re-derive dead ends.

### 2. Verify state

Run what applies. Skip what does not. If a command fails, record `unknown`
— do not invent.

1. `git branch --show-current` + `git status --short` + `git log --oneline -15`
2. `gh pr list --state merged --limit 15` and `gh pr list --state open` when
   this is a GitHub repo
3. Confirm referenced plan docs exist (Glob or `ls`). Capture exact paths.
4. Cross-check: anything the conversation claims merged or shipped must
   match git/`gh`. On disagreement, keep the command output.

### 3. Load the graph

Required: `bd` on `PATH` and a beads database for this project (usually
`.beads/`). If either is missing, stop. Do not `bd init`.

```bash
command -v bd
bd where
bd ready
bd list --status=in_progress
```

If a planner IR exists (`tmp/beads/<program>/planner-ir.json` or the path
the project documents), read it. The program slug is that directory name,
or the `program:` label already on the beads. Do not slurp the whole
database into context.

### 4. Diff — what is not recorded

For each mined item, `bd search "<outcome keywords>"` against titles and
bodies, then classify:

| Class | What to do |
| --- | --- |
| Already a bead (same outcome, including closed) | skip |
| Note on an existing bead (landmine, locked decision, pivot that does not create work) | append notes / comment; do not create |
| Missing work | create and place |
| Missing edge only | add the dep; do not clone the bead |
| Not work (user question, flavor, restating project-doc rules) | Gap only; do not bead |

"Not recorded" means the **outcome** is absent, not that the wording is
new. Treat a near-duplicate title as already recorded.

Do not bead conversation order, project-doc rules (`CLAUDE.md` /
`AGENTS.md` / `CONTRIBUTING.md`), or questions that need the user now.

### 5. Create and place

Create only the **Missing work** rows. Each new bead must be executable by
a fresh agent with no session context: why, a concrete anchor (file, PR,
command), falsifiable success criteria, and a verify command when one exists.

```bash
bd create --json --title "<observable outcome>" --type <task|feature|bug|decision> \
  --parent <epic-id> \
  --description "<why, anchor, success criteria, verify>"
bd dep add <blocked-id> <blocker-id>   # only when the edge is causal
```

Prefer `--parent` plus explicit `bd dep add` over guessing `--deps` shape.

If planner IR exists, do not `bd create` in a way that will fail validate
as manual IR↔bd drift. Prefer `/beads:ingest` when that skill is installed
(it skips near-duplicates); then add parents and remaining causal edges.
Horizon BUILD/COMPOSE beads need WHY and `verification.commands` or
`/beads:validate` will fail.

**Place** means hang the bead on the existing graph, not append it to a
session-order list.

1. **Parent** = the epic or slice that owns this outcome. Parent is
   organization, never a blocker.
2. **`blocks` only for producer → consumer.** The blocker publishes a named
   artifact or state the new bead consumes. Not "comes next," not "same
   file," not the order we talked.
3. **Never `blocks` to or from an epic.** Never let ordinary work depend on
   a verify gate. Gates are sinks.
4. **Cross-slice** edges target the leaf that publishes the artifact, not
   the slice epic or gate.
5. **Pivots that falsify a contract** become a `decision` (or a DISCOVERY /
   CONTRACT-CHANGE title). Block only the affected consumers. Unaffected
   work stays ready.
6. **Landmines** are notes on the bead they affect, unless they *are* a
   spike or fix.
7. **Do not create an epic** unless a program or slice container is
   actually missing.
8. After creates, `bd find-duplicates` on the new titles. Merge or close
   accidental clones before validate.

### 6. Validate

Always. Even when step 5 created nothing.

1. If `/beads:validate` is installed, follow that skill with the program
   slug (or IR path) from step 3.
2. If it is not installed: `bd dep cycles`, and `bin/bead-verify --graph`
   with `--label program:<slug>` when that binary and label exist. Say the
   run used this degraded gate.

A red validate is not a report-and-stop. Fix the beads **this run added**
(illegal edges, missing WHY/verify, parented-as-blocker, clones) and
re-run validate once. If it is still red, leave the beads and report the
failure. Do not delete the graph. Do not keep mutating unrelated beads to
make an old red green.

## Output

Use these sections, in this order. No others.

1. **Gap** — unrecorded items (now beads or notes), already-recorded skips,
   and not-work items left in the session. If nothing was missing, say so.
2. **Created** — one line per new bead: id, title, parent, deps added, why
   this location. Notes-only updates listed separately. `none` if step 5
   created nothing.
3. **Validate** — the command(s) run and the result (green, or the remaining
   failure after one fix pass).
4. **Next** — the first `bd ready` bead the next agent should start (id +
   title), or `none`. No kickoff prompt and no path to a markdown brief.

## Guardrails

- Do not write a handoff markdown file (`handoff-*.md` or otherwise).
- Do not `bd init`. Do not invent beads, PR numbers, or statuses.
- Do not commit, push, or open a PR. Graph edits are the artifact; git is
  the user's.
- Do not dump a conversation-order chain. An edge without a named
  producer/consumer artifact is not an edge.
- Do not restate project-doc rules as beads.
- Edit the bead graph (and planner IR when it exists). Edit nothing else.
- One project per run.
