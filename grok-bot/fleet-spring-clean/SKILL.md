---
name: fleet-spring-clean
description: >-
  Use this when spring-cleaning a multi-bot Grok Bot fleet: Notion company vs
  personal brains, naming/boss tags, boards, daily brief, routine logs,
  CreateAgent rules, skill arsenal, and shareable reorg. Pauses for explicit
  user yes before every mutating batch. Not for one domain's sales strategy.
  Invoke as /fleet-spring-clean [path-to-fleet-config].
---

# /fleet-spring-clean

Declutter a multi-bot Grok Bot fleet: Notion roots, naming, boards, skills,
routines, CreateAgent rules, and a shared skill arsenal. Structure-specific;
brand-agnostic.

Do not delete bots. The human deletes from the sidebar.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates)

Parse:

1. **Path** — a filled fleet config (markdown file or Notion page). Read it
   in full before Phase 0.
2. **Empty** — ask OWNER for the config page, or have them duplicate
   [references/fleet-config-template.md](references/fleet-config-template.md)
   and fill the copy. Do not write values into the blank template in this
   folder.
3. **Empty and no OWNER yet** — stop. Do not invent a roster.

If several fleets are in play, ask which one. One fleet per run.

Out of scope: customer outreach, publishing, or account actions on social
platforms; domain strategy (what the company sells); destroying bots.

## Owner config

Fill once per fleet, in the config copy — never in this skill. Placeholders:

| Placeholder | Meaning |
| --- | --- |
| `OWNER` | Human who bots report to by default |
| `COMPANY_BRAIN` | Top-level Notion page for company / ops |
| `PERSONAL_BRAIN` | Top-level Notion page for non-company life |
| `ARCHIVED` | Child of `PERSONAL_BRAIN` for cold ideas |
| `BUILDER_BOT` | Bot that creates/revises bots (this skill's runner) |
| `CHIEF` | Coordinator bot (if any) |
| `PERSONAL_ASSISTANT` | Personal ops bot |
| `WRITE_HOMES` | Map: role → Notion DB/page |
| `STAGE_SET` | Default: Icebox, Next up, In Progress, Done, Cancelled (+ optional Blocked on OWNER) |
| `OPS_LOCKS` | Standing freezes (e.g. no outbound contact). Note exceptions that must keep running. |
| `ARSENAL_SOURCE` | Optional upstream public skill pack URL to vendor from |
| `ROUTINE_RUNS_DB` | Notion DB for routine execution logs |
| `BOSS_TAGS` | Tag vocabulary for reporting lines (examples: Chief, marketing lead, eng lead) |

## Procedure

Run Phase 0 through Phase 13 in order. Do not skip ahead of an Exit the
OWNER has not agreed. Stay quiet on routine fires that only log `quiet`.

### Confirm before apply (every mutating set)

Read-only work runs without a gate: listing agents, pages, boards, skills,
routines, and drafting a proposal.

Anything that mutates agents, Notion, routines, skills, boards, or names
needs a gate first — including Notion moves, renames, stage schema changes,
routine deletes, UpdateAgent / CreateAgent batches, and skill writes.

Before each phase's Apply (and before every later coherent batch in that
phase):

1. **Propose** — summarize this set: what, where, why. Placeholder names,
   not private URLs.
2. **Wait** — stop. Do not apply until OWNER gives an explicit yes to
   *this* set.
3. **Apply** — only the approved set. The next set (next phase, or another
   batch in the same phase) starts again at Propose.

No blanket yes. "Continue," "do the rest," "it's reversible," or owner-mode
bias-to-act is not permission for later sets. Confirmation every time,
every set.

### Phase 0 — Inventory (read-only)

List and report without a gate:

1. List agents (names, who they report to, archived?).
2. List top-level Notion private pages; flag strays that belong under
   `COMPANY_BRAIN` or `PERSONAL_BRAIN`.
3. List project boards and their Stage/Status options.
4. List skills under `/home/box/agent-data/workflows/` and live routines on
   important bots.
5. Note expired approval cards from the last few hours if OWNER mentioned them.
6. Note connector / plugin auth that is broken or mislabeled (do not rotate
   secrets in this phase).

If the inventory should land on `BUILDER_BOT`'s board (a write), propose
that set, wait for yes, then write. Chat-only inventory needs no gate. Do
not move anything yet.

**Exit:** OWNER agrees the inventory is complete enough to reorg.

### Phase 1 — Two brains + archive

Propose the set, wait for explicit yes, then apply:

1. Ensure exactly two durable roots: `COMPANY_BRAIN` and `PERSONAL_BRAIN`.
   Rename old "misc" roots rather than creating a third.
2. Create `ARCHIVED` under `PERSONAL_BRAIN` (not as a sibling of the brain).
3. Move company pages → `COMPANY_BRAIN`; personal → `PERSONAL_BRAIN`; cold
   personal ideas → `ARCHIVED`.
4. Rename historical journals clearly when moving (pattern: "Business
   Journal prior to YYYY").
5. Update bot descriptions that still name the old roots.

**Exit:** Private sidebar top level shows the two brains (plus system
defaults), not a pile of strays.

### Phase 2 — Naming (one clear boss)

Propose the rename set, wait for explicit yes, then apply:

1. Bots that report only to OWNER: **no owner prefix** in the name (plain name).
2. Bots that report to another bot: front-loaded boss tag from `BOSS_TAGS`,
   e.g. `[Chief]`, `[Marketing]`. Multi-boss (not OWNER): `[Marketing, ...]`
   with literal three dots.
3. If a bot reports to OWNER **and** others, omit OWNER from the tag; show
   only the other bosses.
4. Mark superseded seats ARCHIVED in the name/description; point traffic to
   the live successor.
5. Respect `OPS_LOCKS` (e.g. do not rewrite a locked wellbeing bot beyond
   name hygiene OWNER asked for).

**Exit:** Every warm seat has one clear boss path OWNER can say out loud.

### Phase 3 — Project boards

Propose the board/schema set, wait for explicit yes, then apply:

1. Align project boards to `STAGE_SET`. Prefer **Cancelled** over vague
   "Killed" unless OWNER insists.
2. Funnel boards (pipeline, inbound) may skip Icebox / Next up — do not
   force project stages onto funnels.
3. If a board view hides empty groups, seed stub cards in empty stages
   **or** tell OWNER how to turn off "Hide empty groups" in the Notion UI.
4. Nest the `BUILDER_BOT` work board under `COMPANY_BRAIN`; rename views
   plainly ("Board").

**Exit:** Project boards show the full stage set OWNER expects.

### Phase 4 — Write homes + board monopoly

Propose the filing set, wait for explicit yes, then apply:

1. Publish `WRITE_HOMES` (role → one Notion destination). Role examples, not
   brands: marketing → Pipeline + Content inbox; legal → Legal drafts;
   partnerships → Partner inbound; chief → Decisions log; personal
   assistant → Personal ops; projects → Projects board.
2. One projects monopoly: only the Projects Manager (or equivalent) owns
   the Projects board schema.
3. Archive duplicate "watchlist" pages that were replaced by databases.
4. Seat new bots into sidebar sections when CreateAgent supports
   `section_id`; if UpdateAgent cannot move sections, tell OWNER to drag.

**Exit:** Each role has one obvious place to write.

### Phase 5 — Daily brief labeling

Propose the brief/skill set, wait for explicit yes, then apply:

1. Add YAML frontmatter on skills that should feed a morning brief:

```yaml
daily_brief: true
daily_brief_section: Weather   # short label
daily_brief_order: 10          # lower first
```

2. Create or update skill `daily-brief`: `PERSONAL_ASSISTANT` aggregates all
   `daily_brief: true` skills into one morning message.
3. Pause redundant standalone routines once the section is inside the
   aggregate.

**Exit:** One morning brief owns the sections; no double pings for the same
fact.

### Phase 6 — Routine runs log

Propose the log set (DB + skill + attaches), wait for explicit yes, then
apply. Split into separate sets if OWNER wants them gated one at a time.

1. Under `COMPANY_BRAIN`, create `ROUTINE_RUNS_DB` with at least: Name
   (title), Agent, Routine, Folder, Status (`ok` / `quiet` / `error` /
   `skipped`), Summary, Started, Finished.
2. Create skill `log-routine-run`: every routine fire appends one row.
3. Append that skill to `BUILDER_BOT`, `CHIEF`, `PERSONAL_ASSISTANT`, and
   any bot with standing crons. Confirm each bot updated its prompts
   (approvals may be required).

**Exit:** New routine fires leave a row; quiet runs still log as `quiet`.

### Phase 7 — Encode CreateAgent standing rules

Propose the `BUILDER_BOT` description edit, wait for explicit yes, then
apply. Keep the rules generic:

1. Plain language: relevant, findable, understandable, usable (familiar
   words, short sentences, answer-first). Optional citation: ISO 24495-1.
2. Naming / boss tags (Phase 2).
3. Notion filing: `COMPANY_BRAIN` vs `PERSONAL_BRAIN` vs `ARCHIVED`.
4. `STAGE_SET` for project DBs.
5. `WRITE_HOMES`.
6. `OPS_LOCKS` (including intentional exceptions).
7. `daily_brief` + `log-routine-run`.
8. Sidebar seating caveat (Phase 4).
9. Owner-mode skill + arsenal attach rules (Phases 8–9).

**Exit:** A brand-new bot created tomorrow inherits the clean without
re-deriving it.

### Phase 8 — Owner-mode skill

Draft the skill text without a gate. Propose the write + CreateAgent bake-in
as a set, wait for explicit yes, then apply:

1. Draft (or refresh via an automate-me-style pass) a skill for OWNER's
   working style, e.g. `owner-mode`.
2. Contents: answer-first, plain language, bias to act on reversible work,
   Notion roots, naming, `OPS_LOCKS`, prose preferences. That bias is for
   the *owner-mode* skill, not for this spring-clean run.
3. Bake "follow owner-mode" into every new CreateAgent description.

**Exit:** Owner-mode exists as a skill; `BUILDER_BOT` references it.

### Phase 9 — Shared skill arsenal

Propose each coherent set (vendor copy, index write, routine create,
Icebox cards) separately if they are not one batch. Wait for explicit yes
before applying each set.

1. Vendor chosen reusable skills into `/home/box/agent-data/workflows/`
   (shared by all bots). Prefer structure over pasting whole skills into
   descriptions.
2. Create skill `skill-arsenal`: index of attachable skills + how to give a
   bot an item (UpdateAgent one-liner + Read path; never paste the whole
   `SKILL.md` into the blurb).
3. Suggested buckets (rename to match whatever pack you vendor):
   - **Prose:** cut AI tells; long-form docs; plain restatement
   - **Fleet:** reflect; recall / context rebuild; meeting signal filter
   - **Coding:** concise verified coding bar; decision trail for long runs;
     playbook when no recipe fits
   - **Principles:** subtract before add; encode lessons in structure;
     never block on the human for reversible work; minimize reader load
4. Create a **weekday** fleet-reflect routine on **one** coordinator
   (`BUILDER_BOT` or `CHIEF`): mine learnings → propose skill edits →
   **do not auto-apply** → stay quiet if nothing durable. Never fan out
   reflect to every bot daily.
5. Create a **weekly** arsenal check: diff `ARSENAL_SOURCE` (if any)
   against a local snapshot JSON; propose adds; never auto-vendor without
   OWNER yes.
6. Icebox speculative tools (e.g. custom webhook UIs) as board cards until
   OWNER pulls them forward.

**Exit:** Arsenal index + reflect + weekly check exist; speculative work is
Icebox, not half-built.

### Phase 10 — Noise filters

Propose the filter skill + wiring set, wait for explicit yes, then apply:

1. For noisy recurring meetings (standup, all-hands notes): add a
   signal-filter skill (0–5 "OWNER needs" bullets; count of ignored items;
   no raw dump).
2. Wire it into the owning bot's routine before any digest to OWNER.
3. Optional later: thin `daily_brief` section once the filter is stable
   (its own set, its own yes).

**Exit:** OWNER stops receiving meeting walls.

### Phase 11 — Routine ownership transfer (delete, don't orphan)

When a job moves from bot A to bot B (or a seat is archived), finish the
handoff on **routines**, not only descriptions.

**Inventory** (read-only, no gate): for every agent, list routines (name,
folder slug, schedule/trigger, enabled/paused). Note duplicate folder slugs
or same job name on two bots.

Then propose each handoff set (create/update on the new owner + delete on
the old), wait for explicit yes, then apply:

1. **One owner:** each standing job has exactly one live routine on the bot
   that should run it. Create/update on the new owner first; confirm it
   appears in that bot's live routines.
2. **Delete the old copy** on the previous owner. Do **not** leave it
   paused "just in case" — paused leftovers look like work and can be
   re-enabled by mistake (or still fire if the pause never stuck). Message
   the previous owner to delete if you cannot edit their routines yourself.
3. **Archived seats:** delete or reassign routines on `[ARCHIVED→…]` bots;
   never leave crons firing on archived names.
4. **Finite watches:** delete routines whose end date has passed (even if
   they were supposed to self-delete).
5. **Paused ≠ superseded:** keep intentional pauses (ops locks, product
   waits, spend caps). Only delete when another bot owns the job, the
   project is cancelled/archived, or the watch is expired.
6. **Fleet scan before close-out** (read-only): search all agents for the
   moved job's name/slug; zero copies on non-owners.

**Exit:** No duplicate digests/crons; no paused ghosts of jobs that already
live elsewhere; intentional pauses documented under `OPS_LOCKS` or the
bot's board.

### Phase 12 — Approvals + leftovers

Listing expired cards and moot skips is read-only. Propose each mutating
set (re-trigger, ARCHIVED sweep), wait for explicit yes, then apply:

1. Re-trigger expired approval cards OWNER still wants (same action; do
   not invent workarounds).
2. Skip moot cards (page already exists, permission already granted).
3. Sweep `ARCHIVED` again for leftovers OWNER named.
4. Confirm `CHIEF` and other bots with standing crons finished
   `log-routine-run` appends (read-only check).

**Exit:** No silent blockers; known leftovers parked.

### Phase 13 — Close-out checklist

Read-only report. Any leftover fix is a new mutating set: propose, wait
for yes, then apply.

- [ ] Two brains + `ARCHIVED` nesting correct
- [ ] Boss tags / plain names applied
- [ ] Project `STAGE_SET` aligned; empty columns visible or UI note given
- [ ] `WRITE_HOMES` published
- [ ] `daily_brief` aggregate live; redundant crons paused
- [ ] `ROUTINE_RUNS_DB` + log skill on standing crons
- [ ] CreateAgent rules updated on `BUILDER_BOT`
- [ ] Owner-mode + arsenal + reflect + weekly check
- [ ] Meeting signal filter live
- [ ] Icebox cards for speculative tools
- [ ] Routine ownership: no duplicate/orphaned paused copies of moved jobs
- [ ] Inventory of still-open items handed to OWNER

## Output

Use these sections, in this order, at the end of the run, after any phase
that stops for an Exit, and whenever the run is waiting on a Confirm:

1. **Phase** — which phase just finished or is waiting, and whether its
   Exit held.
2. **Proposed** — the next mutating set, if waiting on yes. Omit if nothing
   is pending.
3. **Changed** — what moved, renamed, created, or deleted *after* a yes.
   Paths and placeholder names, not private URLs.
4. **Still open** — leftovers for OWNER, including approval cards.
5. **Quiet** — routine fires that only logged `quiet` (one line, or `none`).

If the run stops at an Exit or a Confirm, emit those sections for the work
so far and wait. Do not start the next phase or apply the next set.

## Guardrails

- Before every mutating set: propose, wait for explicit yes, then apply.
  Confirmation every time, every set. No blanket yes.
- Do not apply a batch because it is reversible, obvious, or "bias to act."
  Owner-mode bias-to-act does not override this skill.
- Read-only inventory may run without a gate. Writes to boards, agents,
  Notion, routines, skills, or names may not.
- Soft-deleting bots is OWNER-only. This skill never destroys bots.
- Do not fill [references/fleet-config-template.md](references/fleet-config-template.md)
  in git. OWNER fills a copy.
- Keep this file free of personal names, private URLs, customer lists, and
  credentials.
- No third top-level Notion root "for misc."
- `ARCHIVED` is a child of `PERSONAL_BRAIN`, not a sibling.
- Do not fan out "everyone reflect daily."
- Do not paste entire skills into agent descriptions.
- Do not auto-apply reflect proposals without OWNER.
- Do not treat funnel boards like project boards.
- Do not pause the one cron `OPS_LOCKS` explicitly said must keep running.
- When a routine moves, delete the old copy. Do not leave it paused.
- Do not rotate secrets during inventory.
