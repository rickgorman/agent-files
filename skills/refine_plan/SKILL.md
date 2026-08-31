---
name: refine_plan
description: Iteratively refine a markdown implementation plan in place via a concurrent 4-critic map-reduce swarm (cross-vendor host CLIs when present; local Claude agents otherwise) until diminishing returns or 6 cycles. Use when a plan is about to become beads or code, after a first draft or /plan-team, before implementation. Invoke as /refine_plan <path-to-plan.md> [--max N] [--dry-run].
---

# /refine_plan

Iteratively refine a markdown implementation plan in the style of Jeffrey Emanuel's
(@doodlestein) Agent Flywheel "Phase 2: Refine the Plan" loop. Each cycle runs an
adversarial fresh-eyes critique, integrates the worthwhile revisions in place, then
self-judges whether the round produced material improvement. Keep cycling until the
plan converges (diminishing returns) or the cycle cap is hit.

Each cycle is a **map-reduce**: it MAPS a swarm of `SWARM_SIZE` fresh critics over
distinct, complementary angles concurrently, then REDUCES their findings into the plan
and into a carry-forward ledger that seeds the next cycle's swarm.

**Prefer cross-vendor critics, not four copies of yourself.** Each wave dispatches its
`SWARM_SIZE` angle-critiques across four DIFFERENT model families — `opus`, `composer`,
`grok`, `terra` — using whichever provider CLIs are actually on this machine. Seat→angle
pairing is a **random, evenly-distributed permutation each wave** (exactly one seat per
angle when all four families are present). Cross-vendor disagreement is the point: a plan
that survives four different intelligences is converged for real, not just converged from
one model's point of view. Missing families are filled with local Claude agents so the
wave still has four critics. YOU (the session model) remain the orchestrator — you own
the reduce, the integration edits, and the ledger; the critics only critique.

The whole point: **spend cheap planning tokens now to save expensive implementation
tokens later.** A converged plan should survive a re-run almost untouched.

## Input

Arguments: $ARGUMENTS (or `{{args}}` — same slot, whichever the harness interpolates)

Parse:
- **First non-flag token** = path to the plan markdown file. Edit this file IN
  PLACE — the file on disk is the persistent state that makes re-runs idempotent.
- `--max N` = override the cycle cap (default `MAX_CYCLES` below).
- `--dry-run` = run the critique + report findings, but DO NOT edit the file.

If no path is given:
1. Look for an obvious plan doc in the cwd (`PLAN.md`, `docs/plans/*.md`, a recently
   edited `*plan*.md`). If exactly one obvious candidate exists, confirm it.
2. Otherwise ask the user for the plan file path, or to paste the plan (if pasted,
   write it to a file first — `PLAN.md` unless they name one — because file-backed
   state is what gives idempotency across runs).

## Constants

- `MAX_CYCLES = 6` — hard ceiling on refinement cycles (override with `--max`). Lower
  than a single-critic loop on purpose: each cycle now spends ~5× the passes
  (`SWARM_SIZE` map critics + 1 reduce), so it converges in far fewer cycles.
- `SWARM_SIZE = 4` — fresh critics dispatched CONCURRENTLY each cycle, one per angle.
  Equals the seat-family count, so a full roster uses every family exactly once.
- `FAMILIES` — four cross-vendor families. Discovery (Phase R) picks the **latest
  available model in each family** from the live catalog; the preferred IDs below are
  the current target, not a frozen pin. Never ship a stale ID when the catalog has a
  newer one in the same family.

  | seat | family | preferred model | detect |
  |---|---|---|---|
  | `opus` | Claude Opus | `claude-opus-5` (Claude Code alias: `opus`) | `claude` or this harness's Agent tool |
  | `composer` | Cursor Composer | `composer-2.5` | `cursor-agent` |
  | `grok` | Grok 4.x | `grok-4.6` | `grok` |
  | `terra` | GPT-5.6 Terra | `gpt-5.6-terra` | `codex` |

  Stay in these families. Do not substitute Fable, Sonnet, Sol, Luna, or a `-fast`
  variant just because it appeared in a list — pick the latest **non-fast** model
  that matches the family. Fast is a last resort if it is the only listing.

- `CACHE_PATH` — day-long roster cache on this machine:
  `${XDG_CACHE_HOME:-$HOME/.cache}/refine_plan/roster.json`
  (create the directory if needed). Valid for 24 hours from `cached_at`.
- `CRITIC_TIMEOUT = 360s (6 min)` — hard per-invocation cap. A critic still running
  at 6 min is abandoned and its angle is **deferred to the next cycle** (see Step 1).
- `CONVERGENCE_STREAK = 2` — consecutive zero-yield cycles that force a stop.
- Materiality tiers (each proposed change gets exactly one):
  - `transformative` — changes architecture, scope, sequencing, or core approach
  - `material` — meaningfully improves robustness, reliability, performance,
    correctness, feature value, or removes a real risk
  - `incremental` — minor addition, reordering, small clarification
  - `cosmetic` — wording, formatting, typos
- A cycle's **yield** = count of `transformative` + `material` changes — aggregated
  across the whole swarm, after dedup — that were actually integrated. Yield is the
  diminishing-returns signal.
- A change's **corroboration** = how many distinct angles independently proposed it.
  Used to prioritize integration and to flag lone-wolf claims (corroboration 1) for a
  skeptic verify before they earn a spot in the plan.

## Phase R — Roster discovery (before cycle 0)

Once per run, resolve which providers and models this machine can actually call.
Do not hardcode today's IDs as if they will still be right next month.

1. **Cache hit.** If `CACHE_PATH` exists and `cached_at` is < 24h old, load it and
   skip to step 5. If it is stale or missing, continue.
2. **Detect providers.** For each family, the provider is available if its binary
   exists on `PATH` (or, for `opus`, if this harness can spawn an Agent with an
   `opus` / `claude-opus-*` model):

   ```bash
   command -v claude
   command -v cursor-agent
   command -v grok
   command -v codex
   ```

   A missing binary is not an error — that family will be local-fallback.
3. **Enumerate models** with a **5s cap** per list command so a hung catalog cannot
   stall the run. If the list command times out or fails, treat the provider as
   present and use the family's preferred model.

   ```bash
   timeout 5 grok models
   timeout 5 cursor-agent --list-models
   # claude: aliases are `opus` / `sonnet` / `fable` / full ids like `claude-opus-5`.
   # Do NOT run `claude models` — it can hang. Prefer the Agent tool or `claude -p --model opus`.
   # codex: no cheap catalog; probe `codex exec --help` and use `gpt-5.6-terra` if -m is accepted.
   ```

4. **Pick per family.** From that family's enumerated names:
   - Prefer the **preferred model** in the table if it is present (or an obvious
     alias — `opus` for `claude-opus-5`).
   - Else pick the highest version in-family (`claude-opus-5` beats `claude-opus-4-8`;
     `grok-4.6` beats `grok-4.5`).
   - Skip `-fast` / `fast` variants unless that is the only listing.
   - Composer stays on Composer (`composer-2.5`), not a Cursor-hosted Grok/Opus.
   - Terra stays on Terra (`gpt-5.6-terra`), not Sol or Luna.
5. **Write the cache** (even on a hit you already loaded — no need to rewrite). Shape:

   ```json
   {
     "cached_at": "2026-08-31T12:00:00Z",
     "ttl_hours": 24,
     "seats": {
       "opus":     { "available": true,  "bin": "claude",        "model": "claude-opus-5" },
       "composer": { "available": true,  "bin": "cursor-agent",  "model": "composer-2.5" },
       "grok":     { "available": true,  "bin": "grok",          "model": "grok-4.6" },
       "terra":    { "available": false, "bin": null,            "model": null, "reason": "codex not on PATH" }
     }
   }
   ```

   This file is a local cache. Do not commit it. Print one line:
   `roster: opus=claude-opus-5 composer=composer-2.5 grok=grok-4.6 terra=local-fallback`.

Available families dispatch via their host CLI (or Agent tool). Unavailable families
are **local-fallback**: a fresh Claude `Plan` / `general-purpose` agent covering that
angle. The loop is identical either way.

## Dispatch

Critics return text. They must not edit the plan or the repo — you integrate.

Per-family invocation (substitute the **picked** model from the cache). Fire all
four, THEN collect. Wrap each with `timeout 360`.

```bash
# opus — Agent tool in this harness (model: opus / claude-opus-5), or:
timeout 360 claude -p --model claude-opus-5 "$(cat /tmp/refine_${CYCLE}_opus.txt)"

# composer — ask/plan mode so it cannot write the tree:
timeout 360 cursor-agent --print --output-format text --mode ask --model composer-2.5 "$(cat /tmp/refine_${CYCLE}_composer.txt)"

# grok — single-turn headless:
timeout 360 grok -p --model grok-4.6 "$(cat /tmp/refine_${CYCLE}_grok.txt)"

# terra — read-only sandbox:
timeout 360 codex exec -m gpt-5.6-terra -s read-only --skip-git-repo-check "$(cat /tmp/refine_${CYCLE}_terra.txt)"
```

Flag names drift; if a CLI rejects a flag, use that CLI's current non-interactive
equivalent. Do not invent a different model family to make a flag work.

**Collect:**
- **done** → stdout / agent report = that angle's critique.
- **dispatch failure** (binary missing, auth error, 429) → substitute a local Claude
  `Plan` agent for that angle THIS wave. Mark `local-fallback` in the report.
- **still running at 6 min** → abandon it, append its angle to the ledger's
  `deferred` (reason `timeout`) so the NEXT cycle re-runs it first; it contributes
  no critique this wave.
- If **fewer than 2 critics survive** a wave → fill the remaining angles via local
  Claude `Plan` agents so the reduce has a real swarm to work with.

## Before the loop (cycle 0)

1. Read the full plan file.
2. **Self-containment pass** (once): some critics have weak or no repo access and
   see only the plan's own text. Would a model with no access to this repo understand
   the plan? List missing context, undefined terms, unstated assumptions, absent
   background — and any file/symbol/schema the critique will need to reason about.
   Fold that background (including the relevant code excerpts) INTO the plan before
   dispatching. A thin plan yields thin, generic critiques and never truly converges.
3. **Initialize the carry-forward ledger** (in-memory working state, NOT written to
   disk): `rejected` (proposals the reduce step declined — never re-litigate these),
   `open_questions` (unresolved tensions surfaced by the swarm), `angles_covered`
   (lenses used so far, to drive rotation), `deferred` (angles carried from a prior
   cycle's 6-min timeout, with reason — re-run FIRST next cycle). All start empty.
   The plan file stays the only persisted artifact, which is what keeps re-runs
   idempotent.

## The cycle (repeat up to MAX_CYCLES)

For each cycle, announce `Cycle K/MAX`.

### Step 1 — Map: concurrent critique swarm

**1a. Pick this cycle's `SWARM_SIZE` (4) angles.** Take any angles in the ledger's
`deferred` list FIRST (they timed out last cycle and are owed a critique), then fill
the remaining slots with **distinct, complementary angles** picked fresh from the
plan's own domain — do NOT hardcode a fixed list. Draw from lenses like
architecture/sequencing, correctness/edge-cases, failure-modes/premortem,
simplicity/scope-cut, security/abuse, ops/rollout/observability, data-model/migration,
performance/cost, testing/verifiability, consumer-contract/UX/DX,
dependency/integration risk. **Rotate** the fresh picks against `angles_covered` so
each cycle's angles differ from prior cycles where possible — this broadens coverage
over the run instead of re-grinding the same 4. Append the chosen lenses to
`angles_covered`; clear the `deferred` entries you just pulled in.

**1b. Randomly assign seats to angles — evenly.** Produce a fresh random permutation
of the four seats and zip them 1:1 onto the four angles:

```bash
shuf -e opus composer grok terra   # → e.g. "grok\nopus\nterra\ncomposer"
```

Zip that order onto the ordered angle list (angle 1 ← first seat, …). **Record the
wave's seat→angle map** (including which seats were `local-fallback`) — it goes in
the final report. Do not hand-pick; the randomness is what spreads each vendor's
blind spots across different lenses over the run.

**1c. Build one prompt file per angle** at `/tmp/refine_<cycle>_<seat>.txt`, each
containing: the CURRENT full plan text, the carry-forward ledger (`rejected` +
`open_questions`), the ONE angle assigned to that seat, and the critic instructions
block below.

**1d. Dispatch all 4 in parallel** using Phase R's picked bin+model for each seat
(or a local Claude agent if that seat is unavailable). Fire every invocation, THEN
collect — never dispatch-and-wait one seat at a time.

Each critic (host CLI or local-fallback agent) gets these instructions:

> You are one critic in a swarm. Your assigned angle is **{ANGLE}** — drive your
> critique primarily through that lens (other critics cover the other angles).
>
> Do NOT re-propose anything already in the ledger's `rejected` list — those were
> considered and declined. Use `open_questions` to focus where the plan is still soft.
>
> Review this entire implementation plan adversarially with fresh eyes. Do NOT
> assume it is good. Propose your strongest revisions — better architecture, added
> / changed / removed features, simpler approaches, sharper sequencing, killed
> risks — to make it more robust, reliable, performant, and compelling.
>
> Then run a PREMORTEM: it is 6 months out and this plan failed completely. What
> went wrong? Which assumptions were false? What edge cases, integration issues, or
> things users hate did we miss? Fold the likely failure modes into your revisions.
>
> CRITICAL: do not invent changes for the sake of changing. Only propose a change
> if it clears a real materiality bar. If the plan is already strong, say so and
> return few or zero changes.
>
> Return a structured list. For EACH proposed change:
> - what changes and where (quote the target lines)
> - rationale: why it makes the plan better
> - confidence it actually improves things (0–100%)
> - materiality: transformative | material | incremental | cosmetic
> - the concrete edit as a git-diff-style hunk against the plan markdown
>
> End with an overall verdict: CONVERGED (only incremental/cosmetic left) or
> NEEDS-ANOTHER-ROUND.

### Step 2 — Reduce: synthesize the swarm

Collect all `SWARM_SIZE` structured critiques and fold them into one decision set:

1. **Cluster + dedup** proposals by their target lines so the same idea from several
   angles becomes one entry.
2. **Tag corroboration**: record how many distinct angles raised each clustered change.
3. **Resolve conflicts**: when two angles propose contradictory edits to the same spot,
   pick one explicitly and note why in the changelog.
4. **Rank** the surviving changes: corroboration desc → materiality → confidence.
5. **Verify lone wolves**: any `transformative`/`material` change with corroboration `1`
   gets a quick skeptic check before integration — reason it through inline, or spawn one
   short verify subagent prompted to REFUTE it. Drop it if it doesn't survive.
6. **Integrate** every endorsed `transformative`/`material` change, plus any
   `incremental`/`cosmetic` change that is clearly correct and cheap, editing the plan
   file in place (skip ALL edits under `--dry-run`).

Then emit a short changelog grouped as:
- **Wholeheartedly agree** (integrated) — note corroboration count where >1
- **Somewhat agree** (integrated with modification)
- **Disagree** (rejected, with one-line why)

Finally, **update the carry-forward ledger** — this reduced state is the seed for the
next swarm: append every rejected proposal to `rejected` (so the next swarm won't
re-litigate it), any unresolved tension to `open_questions`, and confirm this cycle's
lenses are in `angles_covered`.

### Step 3 — Score the cycle

Compute and print this cycle's aggregate **yield** (integrated transformative + material
changes across the swarm, post-dedup). State it explicitly, e.g.
`Cycle 3 yield: 2 material, 1 transformative (from 4 angles; 1 corroborated ≥2)`. Also
note any angles that **timed out → deferred** and any that ran as **local-fallback**
this cycle — yield is computed only over critiques that actually returned.

## Stop conditions (diminishing returns — self-judged)

Stop the loop when ANY of these is true:
1. **Converged**: a cycle's yield is `0` (no transformative or material change
   survived) — the critique is only turning up incremental/cosmetic items.
2. **Streak**: `CONVERGENCE_STREAK` consecutive cycles each with yield `0` (belt and
   suspenders for case 1).
3. **Cap**: `MAX_CYCLES` (6) reached.
4. A **majority of the swarm** returns verdict `CONVERGED` two cycles running.

With a 4-angle swarm, a single zero-yield cycle is already strong convergence evidence
— four independent lenses found nothing material. `CONVERGENCE_STREAK` stays at 2 only
as belt-and-suspenders.

**Final-cycle leftovers.** When the loop stops (any condition above), any angle still
sitting in `deferred` — i.e. it timed out on the last cycle and there is no next cycle
to absorb it — is **reported as uncovered**, not retried. No extra retry wave is spun
up; the run ends with an honest note that that lens went uncritiqued.

Be honest about yield. Inflating it to keep cycling, or inventing churn on an
already-good plan, breaks the idempotency guarantee. On a re-run of an
already-refined plan, cycle 1 SHOULD report yield 0 and stop — that is correct
behavior, not failure.

## Final report

Print:
- plan file path
- the **roster** actually used (picked model per family, and which seats were
  `local-fallback`)
- cycles run and why it stopped (converged / streak / cap)
- per-cycle yields, e.g. `4, 2, 1, 0`
- the **seat→angle assignment per cycle** (showing the random even rotation — which
  vendor covered which lens each wave), plus a one-line corroboration note (how many
  integrated changes were flagged by ≥2 angles)
- any **timeouts → deferrals**, any **local-fallback** angles, and any **uncovered**
  angles (deferred with no next cycle)
- a tight summary of the material changes made across all cycles
- if `--dry-run`: note that nothing was written and the diffs were report-only

Then, if the file is in a git repo, suggest the user `git diff -- <plan>` to review.

## Guardrails

- Edit ONLY the plan file. Do not touch source code, run migrations, or implement
  anything — this skill refines the plan, nothing else.
- Never delete the user's intent. Refine and harden the plan; don't replace it with
  your own different plan.
- Preserve the plan's existing structure/headings unless restructuring is itself a
  `transformative` improvement (and then say so in the changelog).
- Keep cycling autonomously to a stop condition — do not pause for confirmation
  between cycles unless a change would be destructive or reverses a stated user
  decision.
- **Dispatch the whole wave concurrently** — fire all `SWARM_SIZE` invocations, THEN
  collect. Never dispatch-and-wait one critic at a time; sequential calls waste the
  whole point of the map step.
- Do not couple this skill to any one app, daemon, or env token. Host CLIs + the
  Agent tool + local-fallback are the whole transport. Missing providers degrade;
  they do not abort the run.
- The carry-forward ledger (including `deferred`) is in-memory working state only. The
  plan file stays the single persisted artifact, so a re-run of an already-refined
  plan still converges to yield 0 on cycle 1 — seat randomness must NEVER manufacture
  churn to keep cycling.
