---
name: generate-grok-bot-map
description: >-
  Rebuild grok-bot/grok-bot-hero.png from the package registry: read
  .claude/data/grok-bot-map.yaml, emit one GenerateImage description that
  amalgamates every published grok-bot package as a site on one waterworks
  frontier, then (when OWNER asks) generate and save at exactly 2172×724.
  Use after adding/removing a grok-bot package, when the section hero is stale,
  or on /generate-grok-bot-map. Learned from /generate-world-map + skill-map.yaml.
---

# /generate-grok-bot-map

How to rebuild `grok-bot/grok-bot-hero.png` — the single picture at the top of
`grok-bot/README.md` showing every published Grok Bot package as one place on
one frontier waterworks. Same *shape* as `/generate-world-map` +
`.claude/data/skill-map.yaml`, adapted for Grok Bot:

| Root agent-files | Grok Bot tree |
| --- | --- |
| `skills/` + `skill-map.yaml` | `grok-bot/` + `grok-bot-map.yaml` |
| `/generate-world-map` → ChatGPT | `/generate-grok-bot-map` → GenerateImage in Grok Bot |
| `world-map.png` at repo root | `grok-bot/grok-bot-hero.png` |
| Do not touch for this skill | Do not edit `world-map.png` |

The prompt/description stays in the session (or ephemeral); the PNG is what
commits. Never put the long prompt on the PR body as the primary path.

## Regenerate when the roster changes

The section hero is a function of one file:
[`.claude/data/grok-bot-map.yaml`](../../data/grok-bot-map.yaml). A package
added under `grok-bot/` without an entry vanishes on the next regeneration.
`/add-new-grok-bot-skill` must write the entry; this skill turns entries into
a picture.

Regenerate when: a package is added or removed, a region changes, or an edge
appears. Do not regenerate for a wording tweak inside a package.

## Read the registry

```bash
cat .claude/data/grok-bot-map.yaml
ls grok-bot/
```

Cross-check: every `grok-bot/<name>/` folder (except README + section hero)
has an entry; every entry has a folder. Mismatch → stop and say so.

Drop any region no package claims.

## Canvas

Committed size must match root `world-map.png` **exactly**: **2172×724**.
GenerateImage may only offer `16:9` — generate wide, then cover-crop/center to
2172×724. Verify with PIL before commit. Type floor at ~900px display: no
glyph under ~28px in the 2172-wide file; title ~140px.

## Attach references

1. Current `grok-bot/grok-bot-hero.png` if it exists — composition reference,
   not a layout to clone.
2. Each package's `*-hero.png` — **mechanism** references: understand the
   machine, then **simplify to map-scale**. One silhouette, one slash plaque.
   Do not paste miniature package heroes into the map.

## Label budget

Permitted on-image words only:

- One title cartouche: registry `title` (e.g. `Grok Bot skills`). No subtitle.
- One giant uppercase banner per drawn region (`banner`).
- One plaque per package (`plaque`, slash included).
- Local mechanism plates only if `structure:` named them.

Ban: SOURCE, CRUX, PAUSE, CONFIRM (unless a package's plaque), edge verbs,
legends, captions, fake UI text, stats boxes.

## Characters + style

Teardrop orb-bots on water infrastructure (canals, flumes, pumps, sluices,
pipes). Light/cubes only as rare flow inside those pipes. One cyan trunk per
registry `blue:`.

## Write the GenerateImage description

Follow registry fields like world-map does:

- Subject: registry `title` — the published package roster as one waterworks
- Kind: elevated scenic poster (~3:1), one continuous world — not a flowchart
- Topology: relay along one water trunk (`blue:`)
- Per package: `structure:` what stands there, `transform:` what the trunk does,
  `plaque:` the sign. Each package sits **inside its region**.
- Compose five or six large masses with open ground between sites.

Emit one fenced `text` block for GenerateImage. Outside: dimensions 2172×724,
permitted words, save path `grok-bot/grok-bot-hero.png`.

## After generate

1. GenerateImage (16:9 ok) + orb reference.
2. Cover-crop to exactly 2172×724.
3. Write `grok-bot/grok-bot-hero.png`.
4. `grok-bot/README.md` line 1: `![grok-bot](grok-bot-hero.png)`.

## Guardrails

- Function of `grok-bot-map.yaml` only — do not invent packages.
- Do not edit `world-map.png` or Claude `skills/` heroes.
- Exact 2172×724. One continuous world, not a collage of package heroes.
- Never put typography instructions (e.g. ALL-CAPS, banner, plaque) on-image — only the actual label words.
