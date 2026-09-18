---
name: transcript-heatmap
description: >-
  Score a long transcript five minutes at a time and render it as a sheet-music heatmap:
  one page where every chunk is a note, colour is the category, dot size is how deep that
  chunk goes, and clicking a note opens the transcript at that moment. For livestreams,
  conference days, podcast back catalogues, all-hands recordings, or any recording too
  long to watch twice. Use when asked for a transcript heatmap, a density map of a stream,
  "where are the good parts", or a way to find the signal in hours of talk.
  Invoke as /transcript-heatmap <path|paths> [--chunk 5m] [--bar 4h] [--out page.html].
---

# /transcript-heatmap

Cut a recording into fixed time slices, score every slice against a rubric you write from
the source itself, and render the whole thing as one page of staves: a bar is a few hours,
a note is one slice, colour is category, dot size is the tier that slice reaches. The page
is the deliverable — a reader scans for the dense passages and clicks straight into the
transcript there.

The rubric is the skill. A heatmap of a rubric that does not fit the source is a pretty
picture of nothing.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}`, same slot, whichever the harness interpolates).

Parse:

1. **Targets** — every non-flag token, each one a **part**, in argument order. A part is a
   file or a directory of cue files: one day, one session, one episode. Parts are the page's
   top-level sections. Plain text, SRT, WebVTT, Whisper output, and YouTube transcript dumps
   all work; a source with no timestamps is placed by word count.
2. **`--label <text>`** — repeatable, pairs positionally with the targets. Default `Part N`.
3. **`--chunk 5m`** — slice length. **`--bar 4h`** — how much time one bar of the stave holds.
4. **`--rubric <file.json>`** — reuse an existing rubric instead of writing one. Only for a
   later part of a source you already scored.
5. **`--scorer "<command>"`** — score through an external classifier instead of subagents.
   Contract: [references/scorer.md](references/scorer.md).
6. **`--out <file.html>`** — write the page to this path instead of publishing an artifact.
   Also implied when the harness has no Artifact tool.
7. **Empty** — use the transcript already in the conversation; write it to a file first.
   If there is none, ask. Do not pick a random file from the repo.

One page per run. Work in a scratch directory, not the user's repo.

## Constants

- Slice `5m`, bar `4h`. Under two hours of source, drop to `3m` slices and a `1h` bar.
- 3–4 categories (2–6 supported). They must partition what this source is about, not what
  its topic is in general.
- One shared tier ladder, 5 rungs (3–6 supported), lowest to highest. The default ladder —
  `noise`, `mention`, `demo`, `explained`, `masterclass` — fits teaching content; rename it
  when the source is not teaching anything.
- Scoring batch: 20 chunks per subagent, 4–6 subagents at a time, one ledger file each.
- Run files: `chunks.jsonl`, `rubric.json`, `scores-*.jsonl`, `page.html`.
- Rubric schema: [references/rubric.example.json](references/rubric.example.json).
  Scorer contract: [references/scorer.md](references/scorer.md).

## Procedure

1. **Chunk first.**

   ```bash
   python3 scripts/chunk.py <source>... --label "Day 1" --chunk 5m --out chunks.jsonl
   ```

   Read the summary it prints: detected format, chunk count, span, median words per chunk.
   A median under ~150 words means the parser found the wrong timestamps — fix the input,
   not the numbers. Note in the census when times were estimated from word count.

2. **Read the source before you name anything.** Read 6–10 chunks spread across every part,
   including the start and the end. You are looking for what this recording actually spends
   its time on and the words the speakers use for it.

3. **Write `rubric.json`.** Categories come from step 2. Each gets `label`, `instructions`
   (what counts, what does not, in the source's own vocabulary), and one `criteria` line per
   tier. Tiers are mutually exclusive and describe the **highest** level anything in the
   slice reaches. Add a `context` paragraph naming what the recording is — every scorer sees
   it before every chunk. Say explicitly what does *not* count for the categories that
   attract false positives.

4. **Calibrate on 8 chunks** before spending the full run: pick a few you expect to be dead
   and a few you expect to be the best in the source, score them, and look. Everything on one
   rung, or the dead chunks scoring high, means the criteria are wrong. Fix the criteria and
   re-score those 8. Throw away calibration scores that came from a rubric you then changed.

5. **Score every chunk.** Default lane, no keys needed: dispatch subagents, each with the
   rubric, one batch of chunks, and the instruction to return one ledger row per chunk —
   `{"id", "part", "chunk_index", "start_s", "words", "categories": {"<key>": {"tier",
   "tier_index", "expected", "confidence"}}}` — appended to its own `scores-<n>.jsonl`. A
   scorer picks a tier per category for each chunk and nothing else; it does not summarise,
   does not skip chunks, and does not rewrite the rubric. With `--scorer`:

   ```bash
   python3 scripts/score.py --chunks chunks.jsonl --rubric rubric.json \
     --out scores.jsonl --cmd "<command>" --workers 8
   ```

   Both lanes are resumable: a rerun scores only the ids that are missing.

6. **Build the page.**

   ```bash
   python3 scripts/build.py --chunks chunks.jsonl --scores scores-*.jsonl \
     --rubric rubric.json --shell references/shell.html --out page.html [--standalone]
   ```

   `--standalone` for a local file; omit it for an artifact publish, which supplies its own
   skeleton. `--sqlite heat.sqlite` when the user wants the scores queryable.

7. **Look once, then ship.** Open the page. Check that the dense bars are the passages you
   remember from step 2 — if the map disagrees with what you read, the rubric is wrong and
   the page is not the fix. One pass of edits, then publish the artifact (favicon, one-line
   description) or write `--out`.

## Output

1. **Link or path** — the artifact URL, or the written file path.
2. **Census** — parts, chunks, slice and bar length, scored/total, categories, and the tier
   distribution per category. Name any chunk that failed to score.
3. **Rubric** — the categories and the tier ladder, one line each, so the reader knows what
   the colours mean without opening the page.
4. **Assumptions** — estimated timestamps, merged or dropped sources, speaker guesses.

## Guardrails

- Never invent a score, and never fill a gap to make the page look complete. Unscored is a
  real state; the page draws it as unscored and the census counts it.
- Do not re-score a chunk because its tier looks wrong on the page. Either the criteria
  change and everything is re-scored, or the score stands.
- One rubric per source. Reusing another recording's rubric without redoing step 2 produces
  a map of the old recording.
- Do not paste transcript text into the conversation. It goes in the page.
- Scorers read; they do not edit `rubric.json`, `chunks.jsonl`, or each other's ledgers.
- Copy `references/` for a run; never modify the shell, CSS, or JS in place to suit one page.
- Write only into the run directory and `--out`. Edit nothing else in the repo.
