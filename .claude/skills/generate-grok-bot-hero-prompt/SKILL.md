---
name: generate-grok-bot-hero-prompt
description: >-
  Write a GenerateImage description (or make a hero PNG) for a grok-bot/
  package: extract the skill's real crux by importance, apply the
  waterworks+orb style, and de-emphasize secondary process like pause
  gates. Use when adding a grok-bot hero, after SKILL.md exists, or on
  /generate-grok-bot-hero-prompt <path|name>.
---

# /generate-grok-bot-hero-prompt

Read a Grok Bot package (`SKILL.md` + README) and emit a **paste-ready
GenerateImage description** for its hero banner. Then (when OWNER asks)
run GenerateImage and save `<name>-hero.png` beside the README.

Authoring only. The PNG lands in `grok-bot/<name>/`. The description
stays in the session — do not commit it, and do not paste it onto the PR
as the primary path.

Style lives in [.claude/grok-bot-folder.md](../../grok-bot-folder.md).
This skill does not restate the whole rubric. It picks the **crux** so
the banner shows what the skill *does*, not its ceremony.

## Style lock (always)

- Frontier Systems Cartography **subset**: old-west / steampunk world.
- Orb-bots (teardrop, black pill eyes, cyan accent orb) always work on
  **water infrastructure**: waterways, canals, aqueducts, flumes,
  plumbing, pumps, valves, cisterns, water towers, sluice gates,
  troughs/pipes that traditionally carry water.
- **Occasionally** light, floating orbs, energon-like cubes, or luminous
  pulses may **emanate from** those water-carrying structures. Waterworks
  are the chassis; light/cubes are rare cargo in the pipes.
- Aspect: prefer `16:9` (Grok Bot GenerateImage). Reference
  [.claude/data/grok-bot-orb-reference.png](../../data/grok-bot-orb-reference.png)
  (the red teardrop orb mascot) when available.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates)

Parse:

1. **Path** — a `grok-bot/<name>/` folder or a `SKILL.md` inside one.
2. **Name** — a published package name. Use `grok-bot/<name>/`.
3. **Empty** — use the grok-bot package already in this conversation. If
   there isn't one, ask. Do not pick a random package.

If several packages match, ask which one. One package per run.

## Procedure

1. **Read** `SKILL.md` and the README Overview in full. Skip Guardrails
   minutiae unless they *are* the product.
2. **Gist by importance** — write three bullets privately, then keep only
   the top one as the **visual crux**:
   - What does this skill *do* for the OWNER's fleet? (promise)
   - What transforms? (messy → ordered, raw → refined, many → one, …)
   - What is *supporting* process (confirmation gates, logging, YAML
     flags)? Mark these **secondary** — they must not dominate the
     picture.
3. **Pick topology** that matches the crux (forge/refinery, gated
   passage, hub-and-spoke, vault, …). Prefer one topology.
4. **Compose** left / center / right for a wide banner:
   - Left: identity + before-state of the crux
   - Center: the defining transformation (the crux machine)
   - Right: after-state / outcome
5. **On-image words** — at most 4–6 labels, taken from the skill's real
   terms for the **crux** (e.g. `/fleet-spring-clean`, `COMPANY_BRAIN`,
   `PERSONAL_BRAIN`). Do **not** put secondary process words on big signs
   unless OWNER insists (e.g. do not make `PAUSE` / `CONFIRM` the hero of
   a spring-clean banner).
6. **Emit** one GenerateImage `description` string (and optional
   `reference_image_paths` note) in a fenced `text` block. Outside the
   fence: package name, save path `grok-bot/<name>/<name>-hero.png`,
   aspect `16:9`, permitted on-image words, and the one-line crux you
   chose.
7. If OWNER says generate: call GenerateImage with that description +
   orb reference; write the PNG next to the README; set README line 1 to
   `![<name>](<name>-hero.png)` (no H1). Do not rescale 16:9 to ~3:1
   unless OWNER asks.

## Output

Use these sections, in this order:

1. **Crux** — one sentence.
2. **Secondary (de-emphasized)** — short list of what must not dominate.
3. **GenerateImage description** — fenced `text`.
4. Optional: generated PNG path.

## Guardrails

- Source-first: open the skill; do not invent a different product.
- Importance over ceremony: UX pauses, flags, and logging are rarely the
  crux.
- Do not commit image prompts into the package folder; the PNG and
  README embed are enough.
- Do not put hero prompts on the PR body as the primary path — generate
  in Grok Bot.
- One package per run.
