---
name: expandable-reader
description: >-
  Turn source material (a file, several files, a URL, a transcript, or what is already in the conversation)
  into one drill-down HTML page: a world-map paragraph on top, toggle sections under it, and clickable
  highlighted phrases that expand in place into deeper nuggets. For a reader with a variable amount of time
  who wants the overview first and chooses where to go deeper. Use when asked for an expandable reader,
  a drill-down summary, a field guide, a layered overview, or "let me dive where I choose".
  Invoke as /expandable-reader PATH|PATHS|URL|TEXT [--lens TOPIC] [--out FILE.HTML].
---

# /expandable-reader

Read the source in full, distill it into a typed tree of nuggets, render that tree into one self-contained HTML page with a world-map paragraph, toggle sections, and click-to-zoom phrases, then publish it as an artifact (or write the file when asked). The leaves are not quotes or recaps. They are things a reader can use: a tactic, a lesson, a mechanism, a caveat, or a revealing moment.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}`, same slot, whichever harness interpolates).

Parse:

1. **Targets** — every non-flag token. A local path (file or directory), several paths, a URL, or pasted text. A directory means every readable text file in it. Several targets are one source set for one page.
2. **`--lens <topic>`** — optional. Names a theme (for example `security`, `cost`, `hiring`) that gets its own sections, extracted in a separate pass so it is not diluted across the rest. Repeatable.
3. **`--out <file.html>`** — optional. Write the page to this path instead of publishing an artifact. Also implied when no Artifact tool exists in the harness.
4. **Empty** — use the source already in the conversation. If there is none, ask. Do not pick a random file from the repo.

One page per run.

## Constants

- Kinds: `tactic` (copyable how-to), `lesson` (principle, usually earned by failure), `mechanism` (how it actually works), `caveat` (risk, limit, gotcha, ethical line), `moment` (an event that reveals something; use sparingly).
- Shape: crux 2–3 paragraphs, about 250 words, 8–14 zoomable phrases. 6–9 sections in source order. 3–7 nodes per section. Depth at most 3 (section → node → children or zoom → grandchildren).
- Prune rule (from `/dag-reader`): a leaf survives only if it does work no sibling does. Prefer 5 sharp nodes over 9 soft ones.
- Schema and renderer contract: [references/schema.md](references/schema.md). Renderer: [references/shell.html](references/shell.html). Merge script: [scripts/build.py](scripts/build.py).

## Procedure

1. **Read every target in full** before extracting anything. Long sources in chunks until the end. A transcript, a repo, or a paper are all fine; note the medium in the subtitle.
2. **Pin the cast and the units.** Who speaks or acts, what the source's own timestamps, line numbers, section labels, or version numbers are. Those units go into node text in mono form, for example `(7:38)` or `(§4.2)`, so a reader can go back to the source.
3. **Partition by lens (only if `--lens` given).** Dispatch one subagent per lens with `references/schema.md` and the full source. It writes `<lens>.json` (`{ "sections": Section[] }`), a `<lens>_index.json` reference list of every passage it considered (time or location, topic, one line, which node used it), and a `handoff.md` naming what it claimed. Then dispatch one subagent for the remainder with that handoff so nothing is claimed twice. Without `--lens`, do the whole extraction in one pass (subagent or in-session).
4. **Write the tree** as `content.json` matching `references/schema.md`: `title`, `subtitle`, `legend`, `crux`, `sections`. The crux is the world map: readable alone in two minutes, with the zoomable phrases being exactly the things a curious reader would click. Every node line is one sentence. Every leaf is a nugget. Attribute in prose ("Shubh's rule:", "the authors argue"). Plain ASCII quotes, no emoji, no markdown inside strings.
5. **Prune.** Walk the tree once more with the prune rule. Drop recaps, marketing, and anything obvious to the intended reader.
6. **Validate** with `python3 -c 'import json;json.load(open("content.json"))'`. Fix, do not skip.
7. **Build** the page:

   ```bash
   python3 scripts/build.py --shell references/shell.html --content content.json [--lens security.json ...] --out page.html [--standalone]
   ```

   Lens files append their sections after the main sections. `--standalone` wraps the fragment in a doctype and body for a local file; omit it for an artifact publish, which supplies its own skeleton.
8. **Look once, then ship.** One look at the rendered page (artifact preview or a local open). One pass of edits. Then publish the artifact (favicon and one-sentence description) or write `--out`. Do not loop on your own page.

## Output

1. **Link or path** — the artifact URL, or the written file path.
2. **Census** — sections, nodes, zoomable phrases, crux word count, and the lens files if any.
3. **Assumptions** — normalizations you made (names, garbled passages, inferred attribution), one line each.

## Guardrails

- Do not write a file unless `--out` is given or no Artifact tool exists. The artifact is the deliverable.
- Leaves are nuggets, never transcript quotes, never section recaps. If a node reads like a summary, cut it or zoom it into the tactic underneath.
- Do not invent nodes to hit the shape. A thin source yields a thin page; say so in the census.
- Do not read a fraction of the source and extrapolate. The crux is written last, after the whole tree.
- Edit nothing else in the repo. The renderer in `references/` is a template; copy it, never modify it in place for one run.
