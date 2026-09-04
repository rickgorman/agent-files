# Skill folder

What a published skill in this repo is. Follow this when adding or editing anything under `skills/`. Exemplars: `skills/dag-reader/`, `skills/refine-plan/`.

Skills live in `skills/<name>/`. That folder is what people copy. Do not also park a published skill in `.claude/skills/` — `.claude/` here is authoring convention, not the steal path. To port an existing skill into `skills/` and open a PR, run `/add-new-skill` ([.claude/skills/add-new-skill/SKILL.md](skills/add-new-skill/SKILL.md)).

## Start here

```bash
# or: /add-new-skill path/to/existing-skill
cp -R .claude/data/skill-template skills/<name>
```

Then fill it in. Two replace tokens:

| Token | Becomes | Example |
| --- | --- | --- |
| `SKILL_NAME` | slash command and folder name, kebab-case | `dag-reader`, `refine-plan` |
| `skill-name` | hero basename — same string | `dag-reader`, `refine-plan` |

The template has `SKILL.md` and `README.md` only. After the skill text exists, follow [.claude/data/generate-hero.md](data/generate-hero.md) for the banner. Do not invent a placeholder PNG. A skill still containing `SKILL_NAME` is not done.

## Required

```
skills/<name>/
  SKILL.md                 # agent procedure (source of truth)
  README.md                # GitHub steal-page
  <kebab-name>-hero.png    # Frontier Systems Cartography banner
```

`<name>` is the slash command, including its punctuation (`dag-reader`, `refine-plan`). Keep the folder name identical to the command so `cp -R skills/<name> ~/.claude/skills/<name>` just works.

Names are **kebab-case** — lowercase, hyphens, no underscores, no spaces. `dag-reader`, `refine-plan`, `self-review`. The hero is the folder name + `-hero.png`.

## SKILL.md — for the agent

YAML frontmatter, then the procedure. Not a marketing page.

```yaml
---
name: <name>
description: >-
  What it does, in one or two sentences. When to use it. Invoke as /<name> <args>.
---
```

`description` is how harnesses auto-invoke. Put the trigger words here, not only in the body.

Body, in this order:

1. `# /<name>`
2. What the run *is* (one short block). No README recap.
3. **Input** — how to parse `$ARGUMENTS` (and `{{args}}` — same slot). Missing-input behavior. One source / one target per run unless the skill is explicitly multi.
4. Constants, roster, caps — if the skill has any.
5. The procedure, numbered, in run order.
6. **Output** — exact sections or artifacts the run must produce.
7. **Guardrails** — only rules that change what the agent does. No pep talk.

Keep rare-path material out of this file. If a section is not needed on the happy path, it belongs in `references/`.

Do not duplicate the README. Point humans at README; keep SKILL.md as the procedure.

## README.md — for a human on GitHub

No H1. The hero already says the name.

```markdown
![<name>](<kebab-name>-hero.png)

## Overview
## Prerequisites
## Install
## When to use
## Output
```

Overview includes: what it is, the contrast table (the dumb default vs this skill), and a mermaid of one pass / one cycle. Voice matches the repo root: short, stealable, second person.

Install is always:

```bash
gh repo clone rickgorman/agent-files
cp -R agent-files/skills/<name> ~/.claude/skills/<name>
# or into a project:  cp -R agent-files/skills/<name> .claude/skills/<name>
```

then the slash-command examples.

Last paragraph points at `SKILL.md` for the procedure. Do not paste the procedure into the README.

## Hero

File: `<kebab-name>-hero.png` next to the README (not in `assets/`). How to make it is [.claude/data/generate-hero.md](data/generate-hero.md). The prompt never goes on a PR or into git.

README line 1 is the only embed. The repo root README's picture is the world map, not a hero — do not stack a hero there.

## World map entry

The root README opens with `world-map.png`: every published skill as one place
on one frontier. It is generated from `.claude/data/skill-map.yaml`, so a new
skill needs an entry there — `plaque`, `region`, `structure`, `transform`, and
any `edges` to other skills — in the skill's own vocabulary. No entry means the
skill disappears the next time the map is repainted.

Adding the entry is part of adding the skill. Repainting is not: the map costs a
human round-trip through ChatGPT, so batch it. How is
[.claude/data/generate-world-map.md](data/generate-world-map.md); like the hero
prompt, it stays in the session and never reaches a PR.

## Optional — only when the skill needs them

| Path | When |
| --- | --- |
| `scripts/` | A real helper the agent must run. Not a restatement of SKILL.md in bash. |
| `references/` | Specs, schemas, long prompts, examples that would bloat SKILL.md. Skill body points here; it does not copy them. |
| `LICENSE.txt` | Only if this skill is not under the repo MIT. Default: omit; root `LICENSE` covers it. |

Do not add: a second README, a changelog, an `assets/` folder for the hero, a copy of `SKILL.md` under another name, or a `.claude/` inside the skill folder.

## Split of concerns

| Question | Home |
| --- | --- |
| What does the agent do, in order? | `SKILL.md` |
| Why steal this, how do I install it? | `README.md` |
| What does it look like at a glance? | hero PNG |
| Long spec / schema / example dump | `references/` |
| Runnable helper | `scripts/` |
| How a skill folder in *this* repo is shaped | this file |
| Copy-ready skeleton | `.claude/data/skill-template/` |
| Repo index (one bullet per skill) | root `README.md` `## Skills` |
| Where a skill sits on the root world map | `.claude/data/skill-map.yaml` |
| How to generate the hero | `.claude/data/generate-hero.md` (session only — never the PR) |
| How to repaint the root world map | `.claude/data/generate-world-map.md` (session only — never the PR) |
| How to port a skill into `skills/` and open a PR | `.claude/skills/add-new-skill/` |

One home per fact. If a constant lives in SKILL.md, the README may mention it in passing (cull caps, cycle cap) but does not become a second procedure.

## Done when

- [ ] Started from `.claude/data/skill-template` (or matches it)
- [ ] Folder name = slash command
- [ ] No `SKILL_NAME` or leftover `skill-name` token
- [ ] `SKILL.md` has `name` + trigger-rich `description`, then Input → procedure → Output → Guardrails
- [ ] `README.md` starts with the hero, has no H1, and has Overview / Prerequisites / Install / When to use / Output
- [ ] Hero PNG at 2172×724, kebab-named, skill's real terms on the signs (prompt stayed off git and off the PR)
- [ ] `cp -R skills/<name> ~/.claude/skills/<name>` is the documented install
- [ ] Root `README.md` `## Skills` has one bullet: `- [<name>](skills/<name>/) <one sentence>`
- [ ] `.claude/data/skill-map.yaml` has an entry for the skill
- [ ] Nothing in the folder exists only to look complete
