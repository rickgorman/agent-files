---
name: add-new-grok-bot-skill
description: >-
  Port an existing Grok Bot playbook into this repo as a published stealable
  package: conform it to the grok-bot-folder template, strip local coupling,
  and open a PR. Use when adding a grok-bot package to agent-files, publishing
  a fleet playbook, or running /add-new-grok-bot-skill <path|name>.
---

# /add-new-grok-bot-skill

Take a Grok Bot playbook that already exists (a folder, a `SKILL.md`, or the
one in this conversation), reshape it to this repo's published grok-bot
folder shape, and open a PR. Authoring only — the published copy lands in
`grok-bot/`, not here, and not in `skills/`.

Do not invent a package from a vague wish. There must be a source.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates)

Parse:

1. **Path** — an existing local file or directory (`SKILL.md`, a skill folder,
   a playbook markdown).
2. **Name** — a skill name. Search the conversation, then
   `/home/box/agent-data/workflows/`, `~/.grok/skills/`, and any path the
   user named.
3. **Empty** — use the playbook already in this conversation. If there isn't
   one, ask. Do not pick a random package from the repo.

If several sources match, ask which one. One package per run.

Optional: `--name <slash>` overrides the published folder/skill name.

## Procedure

Read [.claude/grok-bot-folder.md](../../grok-bot-folder.md) and
[.claude/data/grok-bot-package-template/](../../data/grok-bot-package-template/)
in full before editing. Those files are the shape. This skill does not
restate them.

### 1. Name it

`<name>` is the Grok Bot `/` skill in **kebab-case** — lowercase, hyphens, no
underscores (`fleet-spring-clean`). Folder = skill so
`cp -R grok-bot/<name> /home/box/agent-data/workflows/<name>` just works.

If the source name has underscores or a `grok-bot-` prefix that would double
up under `grok-bot/`, rename it on the way in and fix the references inside
it — the published roster is kebab-case throughout.

If `grok-bot/<name>/` already exists, stop and say so.

### 2. Strip coupling

The published package has to run on someone else's fleet. While porting:

- Drop personal paths, one person's Notion URLs, and named company pages.
- Drop a hard-coded roster of bots. Replace with placeholders
  (`OWNER`, `BUILDER_BOT`, `COMPANY_BRAIN`) and a blank template in
  `references/` if the run needs a fill-in config.
- Keep the mechanism. Cut the private names, dollar maps, and "Rick" headers.

A package that cannot stand without this user's stack is not ready to
publish. Say so and stop.

### 3. Write the folder

```bash
cp -R .claude/data/grok-bot-package-template grok-bot/<name>
```

Replace `SKILL_NAME` and `skill-name`. Fill `SKILL.md` and `README.md` until
they match the rubric (Input → procedure → Output → Guardrails; README with
hero embed on line 1, no H1, then Overview / Prerequisites / Install /
When to use / Output, contrast table, one mermaid). Strip the template's
hero-style HTML comment. Voice matches the repo root: short, stealable,
second person.

Rare-path material and blank fill-in templates go in `references/`. A real
helper goes in `scripts/`. Do not add a second README, a changelog, or a
hero `assets/` folder. Do not invent a placeholder hero PNG.

Append one bullet to `grok-bot/README.md`, same shape as the lines already
there:

```markdown
- [<name>](<name>/) <one sentence: the mechanism, not a slogan>
```

Point the root `README.md` `## Grok Bot` section at the new package — one
card matching the prompts already there, or one sentence if a card would
repeat the tree index. Do not add a Claude `## Skills` bullet and do not
list `~/.claude/skills/` as the install.

Add one entry to `.claude/data/grok-bot-map.yaml` too — the section hero
is generated from that file, and a package with no entry vanishes the
next time the map is regenerated. Follow the entries already there:
`plaque` (the sign bolted to the worksite — `/<name>`, lowercase, slash
included), `region` (one of the regions declared at the top of the file
— add a region only if none fits), `structure` (what stands at that
site), `transform` (what the blue work does passing through, told
through the building's shape rather than through words), and any
`edges` to other packages.

Do **not** add an entry to `.claude/data/skill-map.yaml`. That roster is
`skills/` only.

Add `grok-bot/<name>/` to the exemplar list in `.claude/grok-bot-folder.md`
only when this package is itself a published exemplar worth naming —
default: skip; `fleet-spring-clean` already sits there.

### 4. Hero

Required.

1. Run `/generate-grok-bot-package-hero`
   ([.claude/skills/generate-grok-bot-package-hero/SKILL.md](../generate-grok-bot-package-hero/SKILL.md))
   on `grok-bot/<name>/`. That skill reads the package, gists by
   importance, and emits a GenerateImage description of the **crux**.
   Secondary process (pause flags, confirm gates, logging) must not
   dominate.
2. Generate the banner **in Grok Bot** (GenerateImage / in-chat) with that
   description plus
   [.claude/data/grok-bot-orb-reference.png](../../data/grok-bot-orb-reference.png).
   Style lock is in [.claude/grok-bot-folder.md](../../grok-bot-folder.md):
   orb-bots on old-west waterworks; light/cubes only as rare flow.
3. Commit `grok-bot/<name>/<kebab-name>-hero.png`. README line 1 is the
   embed; no H1.

The PNG must be **exactly 2172×724**, matching root `world-map.png`. If
GenerateImage only offers 16:9, generate wide then center-crop /
cover-resize to 2172×724. Do not rescale further after that. Do not
invent a placeholder PNG. Do **not** put an image prompt on the PR as
the primary path. Do not follow `generate-hero.md` (that is ChatGPT
for `skills/`).

If a PNG the user named is already on disk, is exactly 2172×724, matches
the waterworks style, **and** shows this skill's crux (not its ceremony),
copy it in (do not rescale). If it is 16:9, center-crop/cover-resize to
2172×724 first. Otherwise generate it in this Grok Bot session (or ask
OWNER to). A package without a hero is not done.

Then regenerate the **section** hero with `/generate-grok-bot-map`
([.claude/skills/generate-grok-bot-map/SKILL.md](../generate-grok-bot-map/SKILL.md))
— same role as `/generate-world-map` after a `skill-map.yaml` entry.
That picture is a function of `.claude/data/grok-bot-map.yaml`, not this
one skill. Do not invent a placeholder PNG. Do not touch
`world-map.png`.

### 5. Branch, commit, PR

Base:

1. `master` if it already contains `.claude/grok-bot-folder.md`.
2. Otherwise the branch that does.

```bash
git checkout -b <name> <base>
```

Stage **file-by-file** (never `git add -A`). `git diff --no-ext-diff`. Commit
without AI attribution lines. Push. Open a PR against that same base.

PR body uses the repo's usual shape (Summary, Changes as a bullet list,
Commit History). Describe the published package. One short line is enough
for the hero (`<kebab-name>-hero.png`, generated in Grok Bot). Do not
paste a ChatGPT image prompt.

## Output

- `grok-bot/<name>/` conforming to the rubric, including the waterworks + orb hero PNG
- one new bullet in `grok-bot/README.md`
- one new entry in `.claude/data/grok-bot-map.yaml`
- a root `README.md` `## Grok Bot` pointer
- a note that `/generate-grok-bot-map` regenerates `grok-bot/grok-bot-hero.png`
- a PR URL

## Guardrails

- Publish into `grok-bot/<name>/` only. Do not copy the result into
  `skills/` or `.claude/skills/` — `.claude/` is authoring skills for this
  repo; `skills/` is Claude.
- Do not edit `.claude/data/skill-map.yaml`.
- Do not commit a hero prompt, a `prompt.txt`, or a ChatGPT dump.
- Do not expand the PR into unrelated packages or rubric refactors.
- One published package per run.
- Edit nothing in the source playbook's original location unless the user asked.
- Keep published files free of personal names, private URLs, and credentials.
