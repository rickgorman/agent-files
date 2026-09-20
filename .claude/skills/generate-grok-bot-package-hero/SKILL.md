---
name: generate-grok-bot-package-hero
description: >-
  Write a GenerateImage description (and optionally make the PNG) for one
  published grok-bot/<name>/ package hero. Extract the skill's real crux by
  importance; apply waterworks+orb style; output exactly 2172×724. Use after
  SKILL.md exists, when adding a package, or on /generate-grok-bot-package-hero
  <path|name>. Not for the section catalog hero — that is /generate-grok-bot-map.
---

# /generate-grok-bot-package-hero

One package → one hero. Parallel to the root repo's per-skill hero path
(`.claude/data/generate-hero.md`), but generated **in Grok Bot** (not ChatGPT)
and sized exactly like `world-map.png`: **2172×724**.

Authoring only. Save as `grok-bot/<name>/<name>-hero.png`. Do not commit the
prompt. Do not touch `world-map.png` or `grok-bot/grok-bot-hero.png`.

## Style lock

See `.claude/grok-bot-folder.md`. Short form:

- Orb-bots (teardrop, cyan accent) on **old-west water infrastructure**.
- Occasionally light / orbs / energon cubes emanate from those pipes.
- Crux of the skill first — not pause gates, flags, or logging.

## Input

`$ARGUMENTS`: path to `grok-bot/<name>/`, or package name. One package per run.

## Procedure

1. Read `SKILL.md` + README Overview.
2. Gist by importance — keep one **visual crux**; mark ceremony secondary.
3. Topology + left/center/right composition for a ~3:1 banner.
4. On-image words: ≤4–6 real crux labels (e.g. `/fleet-spring-clean`,
   `COMPANY_BRAIN`, `PERSONAL_BRAIN`). No `PAUSE` / `CONFIRM` unless that *is*
   the product.
5. Emit GenerateImage description (fenced `text`). Prefer aspect `16:9`.
6. If OWNER says generate: GenerateImage + orb reference → cover-crop/center
   to **exactly 2172×724** → write `grok-bot/<name>/<name>-hero.png`.
7. README line 1: `![<name>](<name>-hero.png)` (no H1).

## Output

1. Crux (one sentence)
2. Secondary (de-emphasized)
3. GenerateImage description (fenced `text`)
4. Optional: PNG path + verified `2172×724`

## Guardrails

- Source-first. One package per run.
- Not the section map — use `/generate-grok-bot-map` for `grok-bot-hero.png`.
- Exact size 2172×724 matching root `world-map.png`.
