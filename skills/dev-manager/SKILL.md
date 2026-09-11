---
name: dev-manager
description: >-
  Division-of-labor doctrine for capacity-weighted multi-provider coding. The
  orchestrator (session model by default; pin with --model) decomposes, judges,
  reviews, verifies, and commits — and never emits product code except
  break-glass. Every implementation task routes to a coder lane by a fixed
  task→model fallback sequence. Spread load by real utilization. Astra
  (gpt-6-astra, xhigh) is the Codex gate lane — plan, architecture, review,
  decompose — host-CLI-first, text-only fallback. Small and everyday emission
  stays Composer / Grok / Opus. Read at the START of any task that will create
  or edit code, before writing a single line. Invoke as /dev-manager
  [--model <name>] [task].
---

# /dev-manager

Standing division-of-labor doctrine for coding work. You are the **orchestrator**
— the **dev-manager**: you decompose, brief, review, verify, commit — and you
**own the continuous orchestration judgment** (which lane, is this diff ok, next
step, done-or-not). That judgment stream stays with you because only the live
session has full state at zero latency and zero external cost. **You do not emit
product code** except the break-glass and trivial-edit exceptions below. Every
line of implementation lands on a coder lane.

Read this at the start of the current coding task, before writing a single line.
Then run the loop. This is not a research skill and not a plan-only skill.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates)

Parse:

1. **`--model <name>`** — pin a specific orchestrator for this run. By
   **default the orchestrator is whatever model is running this session** —
   do not route the judgment stream to a dedicated model; that just adds cost
   and latency. Absent the flag, "the orchestrator" everywhere below = the
   current session model.
2. **Remaining non-flag text** — the coding task to apply the doctrine to.
3. **Empty** — apply as standing doctrine for the coding task already in this
   session. Do not pick a random file from the repo. If there is no coding task
   yet, ask.

One coding task per run. If several unrelated implementation jobs are in play,
ask which one.

## Roster

First choice **bold**; then order of fallback; *italic orchestrator* = break-glass
only (the running/pinned orchestrator model types only as last resort).

| Task | Sequence (first → fallbacks → break-glass) | Why first |
|---|---|---|
| **Orchestrate / judgment** (continuous) | **orchestrator** *(only — never delegated)* | live state, free, instant |
| **Plan / architecture** | routine: single lane — **Opus** *(routine)* → Grok (host) → Astra xhigh *(hard single-lane/gate)*. **hard/ambiguous → extra cross-vendor plan passes** (10 min). **near-impossible / destructive-without-safeties → fuller multi-lane deliberation** (12 min). Break-glass *orchestrator* | single lane for routine; more seats when the plan is contested or the blast radius is large |
| **Decompose** (plan → in-memory task-units) | **orchestrator** ⇄ **Astra** (`gpt-6-astra`, **xhigh**) — **50/50 split, alternate per run**. **NOT composer / grok / opus.** | decomposition is judgment-heavy and full-context; keep it in the high-reasoning pair, never a code-emission lane. Alternate the two to spread load. Astra reached host-CLI-first (`codex exec -m gpt-6-astra`) |
| **Review / adversarial gate** | **Astra** xhigh *(final gate)* → **Opus/Grok** *(routine passes)* → *orchestrator* | cross-family blind-spot catch |
| **Hard code** (concurrency, migration, gnarly debug) | **Opus** → Composer → Grok (host) → *orchestrator* | top repo code-gen quality |
| **General / feature / repo-wide code** | **Composer / Grok / Opus** (even 3-way rotate) → *orchestrator* | spread load; Composer/Grok lead to spare the hottest high-reasoning Claude seat |
| **Everyday / mechanical / frontend** | **Composer** → Grok (host) → Opus → *orchestrator* | fastest throughput; Claude last of the three |
| **Small / simple / one-off edit** | **Composer ⇄ Grok** (rotate) → *orchestrator* | spread off the Codex gate lane |
| **Fast agentic / terminal loop** | **Grok** (host) → Composer → Opus | faster, host drives repo |
| **Text-only plan/patch** (no repo access) | **Grok** (text-only fallback) → Astra (text-only fallback) → *orchestrator* | text-only seats, zero-metered |

**Rotation** — `general code` rotates **Composer / Grok / Opus** in **equal
thirds** (no Opus double-weight — keep Claude's share at parity, not above).
Opus stays first-line only for `hard code`. `small/simple` rotates
**Composer ⇄ Grok**. Rotate per dispatch, or by disjoint file-set when
concurrent. **Astra is a gate lane, not a small-slice emitter** — never burn
a weekly-capped Codex seat on work Composer, Grok, or Opus already owns.

**Break-glass** — the orchestrator emits code **only** after a lane returns
horrible output on the same brief (say so explicitly when it happens).

**Capacity** — spread load by real capacity/utilization across the lanes that
are actually available on this machine. Bias emission away from the hottest
lane. Reserve scarce weekly-capped lanes for gates (plan, review, hard code,
decompose). Do not hard-code a private dollar map; read provider status (or
local session logs if the provider writes them) when you need a utilization
signal.

### Transport (host-CLI first, text-only fallback)

Detect binaries on `PATH`. A missing binary is not an error — fall down the
row, then to a text-only fallback transport if one exists on this machine.

| Lane | Spawn (primary = host) | Fallback transport |
|---|---|---|
| **orchestrator** (session model by default; `--model <name>` to pin) | this session — decompose, judge, review, git, verify | — |
| **Opus** (`claude-opus`) | Agent tool, `subagent_type:"general-purpose"`, `model:"opus"` — repo tools. Host binary: [`claude`](https://github.com/anthropics/claude-code) | — |
| **Composer** (`composer-2.5`) | [`cursor-agent`](https://cursor.com/docs/cli/overview) (or `agent` if that is what is on `PATH`) `--print --output-format text -f --model composer-2.5 "<brief>"` from repo root via Bash | — |
| **Grok** (`grok-4.5`) | host [`grok`](https://github.com/xai-org/grok-build) CLI (repo access, drives the tree like Composer) | text-only fallback if present |
| **Astra** (`gpt-6-astra`) | host [`codex`](https://github.com/openai/codex) `exec -m gpt-6-astra -c model_reasoning_effort=xhigh` from the worktree (`-C <worktree> --skip-git-repo-check`). Gates: add `-s read-only` | text-only fallback if present |

```bash
command -v claude
command -v cursor-agent || command -v agent
command -v grok
command -v codex
```

Effort for Astra is **`xhigh`**, set with `-c model_reasoning_effort=xhigh`
(the override OpenAI documents for `codex exec`). Flag names drift; if the
CLI rejects that `-c` key, use that CLI's current non-interactive effort
override. Do not invent a different model family to make a flag work. Do not
drop Astra below xhigh for a gate; if the weekly-capped Codex lane is hot,
skip the seat and take the next fallback.

**Host CLI first.** If the host binary is missing but a text-only fallback
transport exists on the machine, use it. That transport cannot see the repo —
**pack the file excerpts the lane needs into the brief.** Do not hard-code a
bridge script path or a personal skills path.

### Astra effort

| Lane | Effort | Use |
|---|---|---|
| **Astra** (`gpt-6-astra`) | **xhigh** | plan / architecture / review final gate; hard single-lane plan; decompose pair |

Astra is the only Codex lane. Do not invent a second Codex micro-lane for
everyday emission. Use the host CLI's current effort control; do not invent
a flag.

### Codex conservation

- Astra is a **gate lane** (plan, review, decompose, hard single-lane plan),
  not a general-purpose emitter.
- Never burn a Codex seat on work Composer, Grok, or Opus already owns.
- Before an Astra xhigh gate, check **provider status** (or local session
  logs if available). If the weekly-capped lane is hot, skip it and take the
  next fallback.
- Prefer host `codex exec` over a text-only fallback when the binary is on
  `PATH` — the host drives the worktree.

### What stays with the orchestrator — never delegate

- Lane choice, done-or-not, "is this diff ok"
- The brief (you write it)
- Review of every return — never execute a delegate's plan unreviewed
- Verification (tests, lint, the project's own check)
- `git add` / `git commit` (and the commit message)
- User-facing status, blocks, and asks
- Planning-escalation ownership (you run the extra cross-vendor passes; you
  own the merge)

## Procedure

1. **Parse input.** Pin `--model` if given. Name the coding task (from the
   remaining args, or the task already in session).

2. **Do not type product code yet.** Classify the work against the roster
   table. Announce the orchestrator (session or pin) and the first-choice
   lane.

3. **Read utilization.** If provider status (or local session logs) show a
   lane running hot, bias this dispatch to the next cooler fallback. Reserve
   scarce weekly-capped lanes for gates.

4. **Pre-brief ambiguity gate.** If you cannot name a single **done-when**
   and the files (or a tight file-set) the slice may touch, resolve the
   ambiguity yourself from project docs (`CLAUDE.md`, `AGENTS.md`,
   `CONTRIBUTING.md`) or ask the user. **Do not dispatch a fuzzy brief.**

5. **Plan — match the ladder to difficulty + blast radius.** Extra seats are
   in-skill: more cross-vendor single-lane passes, then you merge. Do not
   call an unpublished sibling skill.

   1. **Routine plan** → one lane (Opus → Grok → Astra xhigh). You read it
      critically and own the adjusted version.
   2. **Hard / ambiguous** (contested approach, unclear decomposition,
      multiple viable architectures) → **orchestrator-owned multi-lane
      review**: dispatch **3 cross-vendor single-lane plan passes in
      parallel** (Opus, Grok, Astra xhigh). You merge → recommended plan +
      tradeoff table. **Timeout: 10 min** — if the wave hasn't returned,
      inspect for a stall and salvage what landed (see quorum below).
   3. **Near-impossible, or destructive without proper safeties**
      (irreversible ops, data/schema loss risk, prod blast radius,
      security-sensitive) → **fuller deliberation** on the same three
      seats. **Timeout: 12 min** — if it hasn't returned, do NOT proceed on
      the risky path; surface the block to the user.

   **On timeout — inspect for a stall, salvage partial quorum.** Do not
   blind-fall-back. If partial data is gatherable:

   - **Hard / ambiguous** — need **≥1 external participant** returned.
     Have it → merge their plan(s) with your own thinking, own the result,
     call it good. **0 external** → escalate to human. Below quorum on a
     merely hard plan, you may still fall back to the best single-lane plan
     if the user isn't reachable.
   - **Destructive / near-impossible** — need **≥2 external participants**
     returned. Have them → merge their input with your own thinking, own
     the result, call it good. **<2 external** → escalate to human. Never
     proceed on the risky action — surface the block to the user.

   You still own the final call on whatever the extra seats return.

6. **Decompose.** Split the owned plan into dispatchable slices. Keep an
   **in-memory task list** (goal, files, done-when per slice). Alternate
   **orchestrator ⇄ Astra xhigh** per decompose run (50/50). Do not hand
   decompose to Composer, Grok, or Opus.

7. **Write the brief + attach the Coder Charter.** One brief per dispatch.

   ```
   TASK CLASS: <row from the roster table>
   GOAL: <one sentence>
   SCOPE: <files / symbols this slice may touch>
   CONSTRAINTS: <project-doc rules that apply; tests that must stay green>
   DONE WHEN: <observable check>
   VERIFY: <commands or behaviors>
   DO NOT: <scope you already ruled out>
   ```

   **Coder Charter** (include in every brief):

   - Implement the brief. Do not expand scope. Do not start a different
     architecture.
   - Stay in the named files unless a dependency forces a hop — then say so
     in the return.
   - Do not `git commit`, `git push`, or open a PR. The orchestrator owns git.
   - Return: files touched, what changed, how you verified, what's left.
   - If the brief is underspecified, stop and say so — do not guess a
     product decision.

8. **Dispatch host-CLI-first** down the row for that task class. Fire the
   invocation, then collect. If the host binary is missing, use the next
   fallback, then a text-only transport if present (excerpts packed into the
   brief).

9. **Review the return yourself.** Diff against the brief and the project
   bar. Routine pass: Opus/Grok. Final / adversarial gate: Astra xhigh. Own
   the verdict. Reject, re-brief the next fallback, or accept.

10. **Verify.** Run the project's check (tests, lint, the commands in
    `VERIFY`). You run them. A coder saying "tests passed" is not verify.

11. **Commit** (you). Stage the files that belong to the slice. Write the
    message. Do not commit unrelated tree dirt.

12. **Next slice or done.** Repeat 4–11 until the task's done-when holds, or
    you are blocked and have surfaced the block.

### Intelligence/second = concurrency

Independent slices with **disjoint file-sets** dispatch in parallel — that
is the throughput lever. Fire the invocations, then collect; do not
serialize work that does not share files. Rotate lanes across concurrent
dispatches (Composer / Grok / Opus in thirds for general code; Composer ⇄
Grok for small). Cap concurrency at what you can actually review as returns
land. Shared-file slices stay serial.

### Exceptions

- **Trivial edit** — typo, import, one-line rename, comment, an obvious
  one-character fix that is cheaper than briefing a lane. Take it, and say
  so. Not a feature, not a refactor.
- **Break-glass** — a lane returned horrible output on the **same** brief.
  You may emit the code. Say `break-glass` and why. One slice, then return
  to dispatch.
- **No lane available** — every host binary missing and no text-only
  fallback. Surface that. Do not silently become the coder.

## Output

Use these sections, in this order. No others.

1. **Orchestrator** — session model, or the `--model` pin.
2. **Lane** — task class, chosen lane, fallbacks skipped (and why: missing
   binary, hot utilization, prior horrible return).
3. **Brief** — the brief you dispatched (or `standing doctrine` if the run
   only armed the loop and has not dispatched yet).
4. **Review** — verdict on the return (accept / re-brief / break-glass).
5. **Verify** — commands run and the result.
6. **Next** — next slice, `done`, or a block for the user.

A standing-doctrine arm (empty args, no dispatch yet) may stop after
**Orchestrator** + **Lane** + **Next**.

## Guardrails

- Do not emit product code except the trivial-edit and break-glass
  exceptions. Judgment stays in this session.
- Never execute a delegate's plan or patch unreviewed.
- Do not dispatch a brief that lacks a done-when and a file-set.
- On a destructive / near-impossible multi-lane plan, **quorum is ≥2
  external participants** returned (Opus, Grok, or Astra — seats other
  than the orchestrator). Below that quorum, do not proceed on the risky
  path — surface the block to the user.
- Do not invent a different fallback table. Missing families degrade down
  the row; they do not rewrite the sequence.
- Edit the task's implementation files via coder lanes, not this skill's
  folder, and not unrelated skills.
- One coding task per run.
