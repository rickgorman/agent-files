---
name: generate-grok-bot-hero-prompt
description: >-
  Write a GenerateImage description (or make a hero PNG) for a grok-bot/
  package or the grok-bot/ catalog: extract the real crux by importance,
  apply the waterworks+orb style, and de-emphasize secondary process like
  pause gates. Use when adding a grok-bot hero, after SKILL.md exists,
  when the catalog changes (`--kind section`), or on
  /generate-grok-bot-hero-prompt <path|name> [--kind package|section].
---

# /generate-grok-bot-hero-prompt

Read a Grok Bot package (`SKILL.md` + README) — or the `grok-bot/`
catalog — and emit a **paste-ready GenerateImage description** for its
hero banner. Then (when OWNER asks) run GenerateImage and save the PNG.

Authoring only. A package PNG lands in `grok-bot/<name>/`. The section
PNG lands at `grok-bot/grok-bot-hero.png`. The description stays in the
session — do not commit it, and do not paste it onto the PR as the
primary path. Do not touch `world-map.png`.

Style lives in [.claude/grok-bot-folder.md](../../grok-bot-folder.md).
This skill does not restate the whole rubric. It picks the **crux** so
the banner shows what the skill *does*, not its ceremony — or, for
`--kind section`, the catalog as a waterworks town, not one package.

## Style lock (always)

- Frontier Systems Cartography **subset**: old-west / steampunk world.
- Orb-bots (teardrop, black pill eyes, cyan accent orb) always work on
  **water infrastructure**: waterways, canals, aqueducts, flumes,
  plumbing, pumps, valves, cisterns, water towers, sluice gates,
  troughs/pipes that traditionally carry water.
- **Occasionally** light, floating orbs, energon-like cubes, or luminous
  pulses may **emanate from** those water-carrying structures. Waterworks
  are the chassis; light/cubes are rare cargo in the pipes.
- Size: **exactly 2172×724** (~3:1), matching root `world-map.png`. If
  GenerateImage only offers 16:9, generate wide then center-crop /
  cover-resize to 2172×724. Do not rescale further after that. Reference
  [.claude/data/grok-bot-orb-reference.png](../../data/grok-bot-orb-reference.png)
  (the red teardrop orb mascot) when available.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates)

Parse:

1. **`--kind section`** (or path exactly `grok-bot/`) — catalog banner.
   Read `grok-bot/README.md` and the package list. Save as
   `grok-bot/grok-bot-hero.png`. Crux is the **district**: the published
   roster as one waterworks town, not one skill.
2. **`--kind package`** (default) — a `grok-bot/<name>/` folder or a
   `SKILL.md` inside one. Save as `grok-bot/<name>/<name>-hero.png`.
3. **Name** — a published package name. Use `grok-bot/<name>/`.
4. **Empty** — use the grok-bot package already in this conversation. If
   there isn't one, ask. Do not pick a random package.

If several packages match, ask which one. One target per run.

## Procedure

1. **Read.** Package: `SKILL.md` and the README Overview (skip Guardrails
   minutiae unless they *are* the product). Section: `grok-bot/README.md`
   plus each published package's one-line promise — not one SKILL.md.
2. **Gist by importance** — write three bullets privately, then keep only
   the top one as the **visual crux**:
   - Package: what does this skill *do* for the OWNER's fleet? (promise)
   - Section: what is the catalog as a place? (a waterworks district of
     the published packages)
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
   fence: kind (`package` or `section`), save path
   (`grok-bot/<name>/<name>-hero.png` or `grok-bot/grok-bot-hero.png`),
   size `2172×724` (match `world-map.png`; if GenerateImage is 16:9,
   center-crop/cover-resize), permitted on-image words, and the one-line
   crux you chose.
7. If OWNER says generate: call GenerateImage with that description +
   orb reference; write the PNG to the save path. Package README line 1
   is `![<name>](<name>-hero.png)` (no H1). Section README line 1 is
   `![grok-bot](grok-bot-hero.png)` (`# grok-bot` may follow). On-disk
   size must be **exactly 2172×724**. If GenerateImage only offers 16:9,
   generate wide then center-crop/cover-resize; do not rescale further
   after that. Do not write `world-map.png`.

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
- One target per run.
- `--kind section` is the catalog, not a package. Do not draw one skill
  as if it were the whole tree. Do not edit `world-map.png`.
