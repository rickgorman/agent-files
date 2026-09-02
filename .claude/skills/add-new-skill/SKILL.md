---
name: add-new-skill
description: >-
  Port an existing skill into this repo as a published stealable skill:
  conform it to the skill-folder template, strip local coupling, and open a
  PR. Use when adding a skill to agent-files, publishing a command from
  ~/.claude, or running /add-new-skill <path|name>.
---

# /add-new-skill

Take a skill that already exists (a folder, a `SKILL.md`, a slash command, or
the one in this conversation), reshape it to this repo's published folder
shape, and open a PR. Authoring only — the published copy lands in `skills/`,
not here.

Do not invent a skill from a vague wish. There must be a source.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates)

Parse:

1. **Path** — an existing local file or directory (`SKILL.md`, a skill folder,
   `~/.claude/commands/foo.md`, `~/.claude/skills/foo/`).
2. **Name** — a slash-command name. Search the conversation, then
   `~/.claude/skills/`, `~/.claude/commands/`, `~/.codex/skills/`,
   `~/.grok/skills/`, and `~/work/*/skills/` / `~/work/*/.claude/skills/` for
   that name. Prefer the longest, current `SKILL.md` (skip `*-old-*`).
3. **Empty** — use the skill already in this conversation. If there isn't one,
   ask. Do not pick a random skill from the repo.

If several sources match, ask which one. One skill per run.

Optional: `--name <slash>` overrides the published folder/command name.

## Procedure

Read [.claude/skill-folder.md](../../skill-folder.md) and
[.claude/data/skill-template/](../../data/skill-template/) in full before
editing. Those files are the shape. This skill does not restate them.

### 1. Name it

`<name>` is the slash command, punctuation included (`dag-reader`,
`refine_plan`, `self-review`). Folder = command so
`cp -R skills/<name> ~/.claude/skills/<name>` just works. Hero file is
kebab-case: `refine_plan` → `refine-plan-hero.png`.

If `skills/<name>/` already exists, stop and say so.

### 2. Strip coupling

The published skill has to run on someone else's machine. While porting:

- Drop personal paths (`~/.claude/rails-conventions.md`, one person's Jira).
- Drop one-app transports (`localhost:3080`, `api.sh`, a single product engine)
  unless the skill *is* that product — in which case it does not belong in
  this repo.
- Replace a hard-coded integration branch with detect (`develop` if it exists,
  else `main`, else `master`, else remote HEAD).
- Load the review/plan bar from the **project** (`CLAUDE.md`, `AGENTS.md`,
  `CONTRIBUTING.md`), not a global personal file. Global `~/.claude/CLAUDE.md`
  may be extra bar if present; project wins.
- Keep the mechanism. Cut the private roster, dollar capacity map, and
  "Rick" headers.

A skill that cannot stand without this user's stack is not ready to publish.
Say so and stop.

### 3. Write the folder

```bash
cp -R .claude/data/skill-template skills/<name>
```

Replace `SKILL_NAME` and `skill-name`. Fill `SKILL.md` and `README.md` until
they match the rubric (Input → procedure → Output → Guardrails; README with
no H1, Overview / Prerequisites / Install / When to use / Output, contrast
table, one mermaid). Voice matches the repo root: short, stealable, second
person.

Rare-path material goes in `references/`. A real helper goes in `scripts/`.
Do not add a second README, a changelog, or a hero `assets/` folder.

Append one bullet to the root `README.md` `## Skills` list, same shape as
the lines already there:

```markdown
- [<name>](skills/<name>/) <one sentence: the mechanism, not a slogan>
```

Do not add a second table, a "When" column, or a per-skill install stanza.
The generic `## Install` block already covers `cp -R skills/<name>`.

Add `skills/<name>/` to the exemplar list in `.claude/skill-folder.md` only
when this skill is itself a published exemplar worth naming — default: skip;
the first two published skills already sit there.

### 4. Hero

Follow [.claude/data/generate-hero.md](../../data/generate-hero.md). Prompt
stays in this session. Never on the PR, never in git.

If `~/Downloads/<kebab-name>-hero.png` (or a path the user named) exists and
is a ~3:1 PNG, copy it to `skills/<name>/<kebab-name>-hero.png`. ChatGPT's
**2172×724** is the on-disk size. Do not rescale.

If there is no PNG yet, still open the PR; the human drops the banner onto
the same branch after. Do not invent a placeholder PNG.

### 5. Branch, commit, PR

Base:

1. `master` if it already contains `.claude/skill-folder.md`.
2. Otherwise the branch that does (usually `skill-folder-template`).

```bash
git checkout -b <name> <base>
```

Stage **file-by-file** (never `git add -A`). `git diff --no-ext-diff`. Commit
without AI attribution lines. Push. Open a PR against that same base:

```bash
gh pr create --base <base> --title "Add a stealable <name> skill" --body-file <path>
```

PR body uses the repo's usual shape (Summary, Changes as a bullet list,
Commit History). Describe the published skill. Do not describe how the hero
was generated. Do not paste a prompt.

## Output

- `skills/<name>/` conforming to the rubric
- a PR URL
- the hero prompt in this session if the PNG was not already on disk
- if the PNG was missing: a one-line note that the banner still needs a drop

## Guardrails

- Publish into `skills/<name>/` only. Do not copy the result into
  `.claude/skills/` — that directory is authoring skills for this repo.
- Do not commit the hero prompt, a `prompt.txt`, or a ChatGPT dump.
- Do not expand the PR into unrelated skills or rubric refactors.
- One published skill per run.
- Edit nothing in the source skill's original location unless the user asked.
