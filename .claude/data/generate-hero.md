# Generate a skill hero

How to make `<kebab-name>-hero.png` for a skill in this repo. The picture follows JoyRudder's unpublished style guide. Do not copy that guide into agent-files. Do not paste it into a published skill folder. Load it from the local checkout.

The generator is **ChatGPT**. This harness does not emit the ~3:1 banner. Your job is a paste-ready prompt **in this session, to the human**. The PNG lands when they drop it in.

Never put the prompt on a PR, in a commit, in the skill folder, or in any other published surface. The prompt is a trade secret.

## Find the style guide

The guide is `skills/image-prompt/SKILL.md` inside a repo named exactly `joyrudder`.

1. If `$HOME/work/joyrudder/skills/image-prompt/SKILL.md` exists, use it.
2. Otherwise look under `$HOME/work` for a directory named `joyrudder` (not `joyrudder-dojo`, not `joyrudder-*`). Use `skills/image-prompt/SKILL.md` there.
3. If it is still missing, **stop**. Say you could not find the local JoyRudder style guide. Do not invent a substitute style. Do not use `~/.claude/skills/image-prompt` as the source — that copy can drift.

```bash
guide="$HOME/work/joyrudder/skills/image-prompt/SKILL.md"
if [ ! -f "$guide" ]; then
  d=$(find "$HOME/work" -maxdepth 2 -type d -name joyrudder -print -quit 2>/dev/null)
  guide="${d:+$d/skills/image-prompt/SKILL.md}"
fi
if [ -f "$guide" ]; then echo "$guide"; else echo "missing: local joyrudder style guide" >&2; exit 1; fi
```

Read that file in full. That file is the style.

## Write the prompt

The skill's `SKILL.md` already exists. Read it (and the README overview). The picture is this skill's mechanism, in this skill's words.

Follow the JoyRudder style guide's procedure:

- Subject: `/<name>`
- Kind: `hero`
- Size: GitHub README **2048×682** (~3:1). Do not change these pixels to match some other tool.
- Emit **one paste-ready prompt** in a fenced `text` block, in the guide's assembly order.
- Do **not** generate with this harness's image tool. ChatGPT is the generator.

On-image words are the skill's own terms. Do not swap a load-bearing word for a prettier synonym. If the skill says `Fact`, the sign says `Fact`, not `Fuel`. If it says `SOURCE`, not `TLDR`. Title is `/<name>`. At most four other text blocks, and only if they are the skill's real labels.

Outside the fence, one line: kind, dimensions, aspect ratio, exact permitted on-image words.

## Give it to the human

Print the fenced `text` block in this conversation. One line outside the fence: kind, dimensions, aspect ratio, exact permitted on-image words, and where to save the PNG (`skills/<name>/<kebab-name>-hero.png`). ChatGPT often returns **2172×724** — that is the on-disk file. Do not rescale.

Do not put the prompt on the PR. Do not commit it. Do not write `prompt.txt` or a ChatGPT session dump.

## After the PNG lands

Save as `skills/<name>/<kebab-name>-hero.png`. Folder names are kebab-case, so the hero basename is just the folder name. ChatGPT's **2172×724** is the on-disk size. Do not rescale it to 2048×682.

README line 1 is the only embed:

```markdown
![<name>](<kebab-name>-hero.png)
```

Do not add the hero to the repo root README. The root README's picture is the world map — `/generate-world-map`.
