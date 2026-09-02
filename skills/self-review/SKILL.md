---
name: self-review
description: >-
  Self-review the current branch diff via a concurrent 3-reviewer swarm,
  accumulating a deduped suggestion list across cycles until new findings dry
  up or 5 cycles. Read-only — never edits code. Use before a human reviewer or
  a PR, on a path, a commit range, or a PR number. Invoke as /self-review
  [target] [--max N] [--out FILE].
---

# /self-review

Iteratively self-review a code change in the style of the `/refine_plan` flywheel,
but **read-only**: the deliverable is an accumulated, deduped list of review
suggestions. This skill never edits the tree. Each cycle MAPS a swarm of
`SWARM_SIZE` fresh reviewers over distinct, complementary angles concurrently,
REDUCES their findings against the running list (keeping only what's NEW), and
re-reviews with rotated lenses. Keep cycling until new material findings dry up
or the cycle cap is hit.

The artifact under refinement is the **suggestion list**, not the working tree.
The diff is frozen. Each cycle the swarm is told what's already found and asked
for only NEW issues. When a cycle adds nothing material, the list has converged.

The point: catch your own bugs and cleanups before a human reviewer (or prod)
does — then you decide what to apply.

Do not write a file unless `--out FILE` is given.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates)

Parse:

- **First non-flag token** = the review **target**. Accepts:
  - a path / glob → review only those files' diff
  - a commit range (`abc123..def456`, `main...HEAD`) → review that range
  - a PR number (`#1387` or `1387`) → review that PR's diff (`gh pr diff`)
  - omitted → the branch diff against the repo's integration branch:
    `git diff <base>...HEAD`. `<base>` is `develop` if it exists, else `main`,
    else `master`, else the default remote HEAD. Announce the resolved base.
- `--max N` = override the cycle cap (default `MAX_CYCLES` below).
- `--out FILE` = also write the final suggestion list to FILE (markdown). If
  omitted, print to the conversation only.

If the resolved diff is empty, say so and stop. There is nothing to review.

## Constants

- `MAX_CYCLES = 5` — hard ceiling on review cycles (override with `--max`).
- `SWARM_SIZE = 3` — fresh reviewers dispatched CONCURRENTLY each cycle, one per angle.
- `CONVERGENCE_STREAK = 2` — consecutive zero-yield cycles that force a stop.
- Severity tiers (each finding gets exactly one):
  - `blocking` — a real bug, security hole, data-loss/corruption risk, broken
    behavior, or a broken consumer contract
  - `material` — meaningfully improves correctness, robustness, performance,
    security posture, or maintainability; or a missing test for a genuinely
    risky path
  - `minor` — small cleanup, naming, idiom, dead code, a non-idiomatic pattern
  - `nit` — pure style, formatting, wording
- A cycle's **yield** = count of NEW `blocking` + `material` findings added to
  the accumulated list this cycle (after dedup against everything already found).
  Yield is the diminishing-returns signal.
- A finding's **corroboration** = how many distinct angles independently raised
  it. Used to rank the list and to flag lone-wolf findings (corroboration 1) for
  a skeptic refute-check before they earn a place on the list.

## Before the loop (cycle 0)

1. Resolve the target and capture the diff (`git diff <base>...HEAD`, a range,
   a path filter, or `gh pr diff`). Read the changed files in full (not just the
   hunks) so reviewers see surrounding context, not just added lines.

2. **Establish intent** (once): what is this change trying to do? Infer from the
   branch name, commit messages (`git log <base>..HEAD --oneline`), and any
   ticket id in those. State it in one or two sentences. Reviewers judge the
   diff against this intent — a suggestion that contradicts the change's purpose
   is out of scope.

3. **Load the bar.** Read the project's convention files before reviewing, in
   this order, whichever exist:

   - `CLAUDE.md` at the repo root, then any nested `CLAUDE.md` closer to the
     changed files (closer wins on conflict)
   - `AGENTS.md`
   - `CONTRIBUTING.md`

   If a user-global `~/.claude/CLAUDE.md` exists, read it too as extra bar;
   project files override it. Extract two buckets and carry both into the swarm:

   - **Micro-style** — naming, formatting, local idiom the files actually state
   - **Structural** — placement, layering, size, responsibility, public-contract
     shape; the rules that catch a change in the wrong layer, not just the
     wrong indent

   Reviewers cite the specific convention they're invoking (file + rule), not
   vibes. If none of those files exist, fall back to idiomatic norms for the
   diff's stack and say so.

4. **Initialize the accumulator** (in-memory working state): `findings` (the
   master deduped suggestion list — the deliverable), `dismissed` (findings a
   refute-check killed, so the next swarm won't re-raise them),
   `angles_covered` (lenses used so far, to drive rotation). All start empty.

## The cycle (repeat up to MAX_CYCLES)

For each cycle, announce `Cycle K/MAX`. The code is frozen across cycles — the
diff under review is identical every cycle. What changes is the review angle
and what's already known, so each cycle hunts for what prior cycles missed.

### Step 1 — Map: concurrent review swarm

Derive `SWARM_SIZE` (3) **distinct, complementary angles** for THIS cycle,
picked fresh from what the diff actually touches — do NOT hardcode a fixed
list. Draw from lenses like correctness/bugs/edge-cases, security/authz/abuse,
performance/queries, data-integrity/transactions/migrations,
simplicity/idiom/convention-adherence, test-coverage/verifiability,
API-contract/consumer-impact, error-handling/failure-modes,
concurrency/race-conditions. Choose the most relevant to THIS diff, and
**rotate** them against `angles_covered` so later cycles probe angles earlier
cycles skipped — with the code frozen, fresh lenses are the engine that finds
new issues. Append the chosen lenses to `angles_covered`.

**Pinned angle:** whenever a conventions file was loaded in cycle 0, ONE of the
three reviewers each cycle is dedicated to **convention-adherence /
idiomatic-structure**, armed with the structural bucket from "Load the bar".
This lens does NOT get rotated out — pin it every cycle and rotate the OTHER
two. Each cycle, vary which slice of the structural checklist this reviewer
leads with so successive cycles probe different rules rather than repeating
one pass.

Then **dispatch all `SWARM_SIZE` subagents in a SINGLE message so they run
CONCURRENTLY** — sequential calls defeat the swarm. Use FRESH read-only or
general-purpose agents so there is no anchoring on prior reasoning. Give each
subagent the diff, the full changed files, the change's intent, the loaded
conventions, the **already-found findings list**, the `dismissed` list, its
ONE assigned angle, and these instructions:

> You are one reviewer in a swarm doing a SELF-REVIEW of a code change before
> it reaches a human reviewer. Your assigned angle is **{ANGLE}** — drive your
> review primarily through that lens (other reviewers cover the other angles).
> You do NOT fix anything; you report findings only.
>
> Here is what has ALREADY been found in prior cycles — do NOT re-report these,
> and do NOT re-raise anything in the `dismissed` list. Find only NEW issues
> through your lens.
>
> Review the diff adversarially with fresh eyes. Do NOT assume it is correct.
> Find real defects and concrete improvements through your lens: bugs, broken
> edge cases, security gaps, slow queries, missing transactions, race
> conditions, broken API contracts, missing tests for risky paths, and
> violations of the loaded convention files. Structural / architectural
> convention violations count as real findings, not nits. Cite the specific
> convention you're invoking.
>
> Then run a PREMORTEM: this code shipped and caused an incident. What was the
> bug? Which input, state, or concurrency interleaving triggered it? Which
> edge case was unhandled? Fold the likely failure into your findings.
>
> CRITICAL: do not invent churn. Only raise a finding if it clears a real
> severity bar and you can name the concrete consequence. Style preferences
> with no real impact are `nit` at most. If you find nothing new through your
> lens, say so and return zero findings — a confident "nothing new here" is a
> valid, useful result.
>
> Return a structured list. For EACH finding:
> - file:line — quote the exact offending code
> - what's wrong and the concrete consequence (the bug it causes / the risk
>   it creates)
> - severity: blocking | material | minor | nit
> - confidence it is a real issue (0–100%)
> - the SUGGESTED fix described concretely (show the replacement code or the
>   approach) — as a recommendation for the human, not an edit you will make
> - if it's a missing test, the test's setup + the behavior it must assert
>
> End with an overall verdict: CLEAN (nothing new but minor/nit) or
> NEEDS-FIXES.

### Step 2 — Reduce: merge new findings into the list

Collect all `SWARM_SIZE` structured reviews and fold them into the accumulator:

1. **Dedup** within the swarm and against the existing `findings` list by
   file:line — the same issue from several angles, or a re-report of a known
   issue, collapses to one entry.
2. **Tag corroboration**: record how many distinct angles raised each new
   clustered finding.
3. **Resolve conflicts**: when two angles give contradictory suggestions for
   the same spot, keep the stronger one and note the alternative.
4. **Verify lone wolves**: any NEW `blocking`/`material` finding with
   corroboration `1` gets a skeptic refute-check — reason it through inline
   against the actual code, or spawn one short verify subagent prompted to
   REFUTE it (default to "not a real issue" unless it can prove the
   consequence). If it doesn't survive, drop it into `dismissed` instead of
   `findings`.
5. **Merge** the surviving new findings into the master `findings` list,
   ranked by severity → corroboration desc → confidence.

Then print a short per-cycle delta: the NEW findings added this cycle
(file:line + severity + one-line description), and note any lone-wolf that
was refuted.

### Step 3 — Score the cycle

Compute and print this cycle's **yield** (NEW `blocking` + `material`
findings added). State it explicitly, e.g.
`Cycle 2 yield: 1 blocking, 2 material new (from 3 angles; 1 corroborated ≥2; 1 lone-wolf refuted)`.
Confirm this cycle's lenses are in `angles_covered`.

## Stop conditions (diminishing returns — self-judged)

Stop the loop when ANY of these is true:

1. **Converged**: a cycle's yield is `0` — the swarm surfaced nothing new that
   is blocking or material (only minor/nit, or nothing).
2. **Streak**: `CONVERGENCE_STREAK` consecutive zero-yield cycles.
3. **Cap**: `MAX_CYCLES` (5) reached.
4. A **majority of the swarm** returns verdict `CLEAN` two cycles running.

With a 3-angle swarm, a single zero-yield cycle is already strong convergence
evidence — three independent lenses found nothing new and material. Be honest
about yield: inventing churn to keep cycling pads the list with noise the
user has to wade through.

## Output

Print:

- the review target and resolved base
- the change's inferred intent (one line)
- cycles run and why it stopped (converged / streak / cap), per-cycle yields
  (e.g. `3, 1, 0`), and the angles used per cycle (showing the rotation)
- **the full suggestion list**, grouped by severity (`blocking` → `material`
  → `minor` → `nit`). For each finding: `file:line`, the consequence, the
  suggested fix, and corroboration count where >1. This is the actionable
  handoff.
- a one-line note on anything a refute-check dismissed and why

If `--out FILE` was given, also write this report to FILE as markdown.

Close by reminding the user the code is UNCHANGED — these are suggestions to
act on. Offer to apply a chosen subset, or to run `/self-review` again later
(a re-run on unchanged code reproduces the same list — that is correct).

## Guardrails

- **Read-only.** Never edit code, specs, or any file except the `--out`
  report file. Never run `git commit`, `git push`, `git add`, or any mutating
  git command. This skill produces suggestions; the user decides what to apply.
- **Dispatch the swarm in ONE message** (all `SWARM_SIZE` agent calls together)
  for true concurrency — firing them sequentially wastes the whole point of
  the map step.
- **Judge against intent, not taste.** A suggestion that contradicts the
  change's purpose, or refactors unrelated code, is out of scope — leave it
  off the list.
- **Lone-wolf blocking/material findings get a refute-check** before they make
  the list — keep uncorroborated, unverified claims out so the handoff stays
  high-signal.
- If the diff changes a public contract (API, serializer, CLI, event shape),
  note the consumer impact as a suggestion. Do not silently skip it, and do
  not "fix" the consumer in this run.
- The accumulator is in-memory working state. Since the code is never mutated,
  a re-run on the same branch reproduces the same list — the command is
  naturally idempotent.
