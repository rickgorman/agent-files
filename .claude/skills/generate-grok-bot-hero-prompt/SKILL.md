---
name: generate-grok-bot-hero-prompt
description: >-
  Retired. Split into /generate-grok-bot-package-hero (one package
  banner) and /generate-grok-bot-map (section catalog from
  grok-bot-map.yaml). Use those instead. Kept as a pointer so old
  invocations still resolve.
---

# /generate-grok-bot-hero-prompt

Retired. This used to do both package and section heroes. Two skills
replaced it — do not keep a third overlapping procedure here.

- One package: `/generate-grok-bot-package-hero`
  ([generate-grok-bot-package-hero/SKILL.md](../generate-grok-bot-package-hero/SKILL.md))
- Section catalog (`grok-bot/grok-bot-hero.png`): `/generate-grok-bot-map`
  ([generate-grok-bot-map/SKILL.md](../generate-grok-bot-map/SKILL.md)) —
  function of [`.claude/data/grok-bot-map.yaml`](../../data/grok-bot-map.yaml)

If invoked as `/generate-grok-bot-hero-prompt --kind section` (or path
`grok-bot/`), follow `/generate-grok-bot-map`. Otherwise follow
`/generate-grok-bot-package-hero`. Do not restate the old procedure.
