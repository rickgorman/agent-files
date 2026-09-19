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
| `skill-name` | optional hero basename — same string | `fleet-spring-clean` |

The template has `SKILL.md` and `README.md` only. A package still containing
`SKILL_NAME` is not done.

## Required

```
grok-bot/<name>/
  SKILL.md                 # agent procedure (source of truth)
  README.md                # GitHub steal-page
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

Heroes are optional. Do not invent a placeholder PNG.

**No hero** (the default on this tree): start with `# /<name>` so the
steal-page has a name.

**Hero present:** line 1 is the embed, and there is no H1.

```markdown
![<name>](<kebab-name>-hero.png)
```

Then the same sections either way:

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

## Hero (optional)

File: `<kebab-name>-hero.png` next to the README (not in `assets/`). How to
make it is [.claude/data/generate-hero.md](data/generate-hero.md). The prompt
never goes on a PR or into git.

A package without a hero is still done. Do not add a fake PNG to look
complete. If a PNG lands later, drop it on the same branch and switch the
README's H1 for the embed.

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
| What does it look like at a glance? | optional hero PNG |
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
- [ ] README starts with `# /<name>` or with a real hero embed — never a placeholder PNG
- [ ] `cp -R grok-bot/<name> /home/box/agent-data/workflows/<name>` is the documented install
- [ ] `grok-bot/README.md` has one bullet: `- [<name>](<name>/) <one sentence>`
- [ ] Root `README.md` `## Grok Bot` points at the package
- [ ] `.claude/data/skill-map.yaml` was not edited
- [ ] Nothing in the folder exists only to look complete
