---
name: SKILL_NAME
description: >-
  What it does, in one or two sentences. When to use it. Invoke as /SKILL_NAME <args>.
---

# /SKILL_NAME

What the run is. One short block. No README recap.

Do not write a file unless asked.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates).

Parse:

1. **First non-flag token** — the target (path, URL, or pasted text).
2. **Flags** — only flags this skill actually has.
3. **Empty** — ask. Do not pick a random file from the repo.

If several targets are in play, ask which one. One target per run.

## Procedure

1. **Read the target in full** before doing the work.
2. **Do the work** in run order. Numbered steps. No marketing.
3. **Stop** when the output contract below is met.

## Output

Use these sections, in this order. No others.

1. **…** —

## Guardrails

- Do not write a file unless asked. If this skill's job is to edit a named file, say that here and name the file.
- Edit nothing else in the repo.
- Do not invent work to fill a cap. A thin input yields a thin run.
