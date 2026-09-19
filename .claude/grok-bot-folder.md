# Grok Bot package folder

What a published Grok Bot package in this repo is. Follow this when adding
or editing anything under `grok-bot/`. Exemplar: `grok-bot/fleet-spring-clean/`.

Packages live in `grok-bot/<name>/`. That folder is what people copy onto a
Grok Bot box. Do not also park a published package in `skills/` or
`.claude/skills/` — `skills/` is Claude, `.claude/` here is authoring
convention, not the steal path. To port an existing playbook into `grok-bot/`
and open a PR, run `/add-new-grok-bot-skill`
([.claude/skills/add-new-grok-bot-skill/SKILL.md](skills/add-new-grok-bot-skill/SKILL.md)).

This file is the sibling of [skill-folder.md](skill-folder.md). Same split
(SKILL.md = procedure, README = steal-page). Different tree, different
install home, no world-map entry.

## Start here

```bash
# or: /add-new-grok-bot-skill path/to/existing-skill
cp -R .claude/data/grok-bot-package-template grok-bot/<name>
```

Then fill it in. Two replace tokens:

| Token | Becomes | Example |
| --- | --- | --- |
| `SKILL_NAME` | Grok Bot `/` name and folder name, kebab-case | `fleet-spring-clean` |
| `skill-name` | hero basename — same string | `fleet-spring-clean` |

The template has `SKILL.md` and `README.md`. Generate
`<kebab-name>-hero.png` in Grok Bot before the package is done. A package
still containing `SKILL_NAME` is not done.

## Required

```
grok-bot/<name>/
  SKILL.md                 # agent procedure (source of truth)
  README.md                # GitHub steal-page
  <kebab-name>-hero.png    # waterworks + orb-bot banner (Grok Bot GenerateImage)
```

`<name>` is the Grok Bot skill name, including its punctuation
(`fleet-spring-clean`). Keep the folder name identical to the skill so
`cp -R grok-bot/<name> /home/box/agent-data/workflows/<name>` just works.

Names are **kebab-case** — lowercase, hyphens, no underscores, no spaces.

Do not put personal names, private URLs, customer lists, or credentials in
the published folder. Owner-specific values live in a filled copy of a
template (usually `references/`), never in `SKILL.md`.

## SKILL.md — for the agent

YAML frontmatter, then the procedure. Not a marketing page.

```yaml
---
name: <name>
description: >-
  What it does, in one or two sentences. When to use it. Invoke as /<name> <args>.
---
```

`description` is how Grok Bot auto-invokes. Put the trigger words here, not
only in the body. Lead with the situation ("use this when…") if that is how
the fleet's other skills are phrased.

Body, in this order:

1. `# /<name>`
2. What the run *is* (one short block). No README recap.
3. **Input** — how to parse `$ARGUMENTS` (and `{{args}}` — same slot).
   Missing-input behavior. One fleet / one target per run unless the skill is
   explicitly multi.
4. Constants, roster, caps — if the skill has any. Placeholders only.
5. The procedure, numbered, in run order.
6. **Output** — exact sections or artifacts the run must produce.
7. **Guardrails** — only rules that change what the agent does. No pep talk.

Keep rare-path material out of this file. If a section is not needed on the
happy path, it belongs in `references/`.

Do not duplicate the README. Point humans at README; keep SKILL.md as the
procedure.

## README.md — for a human on GitHub

No H1. The hero already says the name. Line 1 is the embed:

```markdown
![<name>](<kebab-name>-hero.png)
```

Then:

```markdown
## Overview
## Prerequisites
## Install
## When to use
## Output
```

Overview includes: what it is, the contrast table (the dumb default vs this
skill), and a mermaid of one pass / one cycle. Voice matches the repo root:
short, stealable, second person.

Install is always the Grok Bot workflows home, not Claude:

```bash
gh repo clone rickgorman/agent-files
cp -R agent-files/grok-bot/<name> /home/box/agent-data/workflows/<name>
```

`/home/box/agent-data/workflows/` is the shared skill arsenal on the Grok Bot
box. If a fleet uses a different workflows home, say so in that package and
keep the folder name equal to the skill name.

Then the `/<name>` examples as Grok Bot composer invocations (type `/` in the
Bot). Do not also list `~/.claude/skills/` unless this package is explicitly
dual-install, and then label both paths.

Last paragraph points at `SKILL.md` for the procedure. Do not paste the
procedure into the README.

## Hero (required)

Every `grok-bot/<name>/` ships `<kebab-name>-hero.png` next to the README
(not in `assets/`). A package without a real hero is not done. Do not
invent a placeholder PNG.

Generate the banner **in Grok Bot** (GenerateImage / in-chat). Attach
[grok-bot-orb-reference.png](data/grok-bot-orb-reference.png) and describe
this package's mechanism on old-west water infrastructure. Commit the PNG
into the package folder. Wire README line 1 to the embed. Do **not** paste
an image prompt onto the PR as the primary path. Do not follow
[.claude/data/generate-hero.md](data/generate-hero.md) — that is the Claude
`skills/` ChatGPT path.

Style is a **subset** of Frontier Systems Cartography (old-west / steampunk)
but **distinct**:

- **Always:** orb-bots work on **old-west water infrastructure** — waterways,
  canals, aqueducts, flumes, plumbing, pumps, valves, cisterns, water
  towers, sluice gates, pipes and troughs that traditionally carry water.
  That waterworks is the chassis of every scene.
- **Occasionally:** non-water cargo may **emanate from** those
  water-carrying structures — light, floating orbs, energon-like cubes,
  luminous pulses traveling in glass pipe segments. Water infrastructure
  first; light / orbs / cubes as rare flow through it.
- **Characters:** glossy teardrop **orbs** — rounded bottom, pointed top,
  simple black pill eyes, small cyan accent on the lower side. Orbs may
  vary body color; cyan accent + teardrop silhouette stay constant.
  Reference: [grok-bot-orb-reference.png](data/grok-bot-orb-reference.png)
  (the red Grok Bot orb mascot). Orbs are the Grok Bot agents in that
  world.

Aspect: Grok Bot GenerateImage's closest size is **16:9**. That is
acceptable for grok-bot packages (`fleet-spring-clean-hero.png` is
1280×720). Do not crop or stretch to the Claude-skill ~3:1 (2048×682)
unless OWNER asks later. Keep whatever Grok Bot returned; do not invent a
rescale.

Do not add grok-bot heroes to the repo root README. The root picture is the
Claude skills world map.

## World map

Leave [.claude/data/skill-map.yaml](data/skill-map.yaml) alone. That roster
is `skills/` only. A grok-bot package is not a site on the root map.

## Optional — only when the package needs them

| Path | When |
| --- | --- |
| `scripts/` | A real helper the agent must run. Not a restatement of SKILL.md in bash. |
| `references/` | Specs, schemas, blank templates, long prompts, examples that would bloat SKILL.md. Skill body points here; it does not copy them. |
| `LICENSE.txt` | Only if this package is not under the repo MIT. Default: omit; root `LICENSE` covers it. |

Blank templates in `references/` stay blank of personal URLs and names. The
importer fills a *copy*.

Do not add: a second README, a changelog, an `assets/` folder for the hero, a
copy of `SKILL.md` under another name, or a `.claude/` inside the package
folder.

## Split of concerns

| Question | Home |
| --- | --- |
| What does the agent do, in order? | `SKILL.md` |
| Why steal this, how do I install it? | `README.md` |
| What does it look like at a glance? | required hero PNG (waterworks + orbs, Grok Bot) |
| Orb character reference | `.claude/data/grok-bot-orb-reference.png` |
| Long spec / blank template / example dump | `references/` |
| Runnable helper | `scripts/` |
| How a grok-bot folder in *this* repo is shaped | this file |
| Copy-ready skeleton | `.claude/data/grok-bot-package-template/` |
| Tree index (one bullet per package) | `grok-bot/README.md` |
| Root pointer (one card or sentence) | root `README.md` `## Grok Bot` |
| How to port a package into `grok-bot/` and open a PR | `.claude/skills/add-new-grok-bot-skill/` |
| Claude skills (different tree) | [skill-folder.md](skill-folder.md) + `skills/` |

One home per fact. If a constant lives in SKILL.md, the README may mention it
in passing but does not become a second procedure.

## Done when

- [ ] Started from `.claude/data/grok-bot-package-template` (or matches it)
- [ ] Folder name = Grok Bot `/` name
- [ ] No `SKILL_NAME` or leftover `skill-name` token
- [ ] `SKILL.md` has `name` + trigger-rich `description`, then Input → procedure → Output → Guardrails
- [ ] Published files have no personal names, private URLs, or credentials
- [ ] `README.md` has Overview / Prerequisites / Install / When to use / Output
- [ ] README line 1 is the hero embed, no H1, never a placeholder PNG
- [ ] `<kebab-name>-hero.png` generated in Grok Bot (waterworks + orbs; 16:9 fine)
- [ ] `cp -R grok-bot/<name> /home/box/agent-data/workflows/<name>` is the documented install
- [ ] `grok-bot/README.md` has one bullet: `- [<name>](<name>/) <one sentence>`
- [ ] Root `README.md` `## Grok Bot` points at the package
- [ ] `.claude/data/skill-map.yaml` was not edited
- [ ] Nothing in the folder exists only to look complete
