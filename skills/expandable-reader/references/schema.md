# Content schema

`content.json` is the only input to the renderer. `scripts/build.py` injects it as `window.GUIDE` into `shell.html`.

```
Guide   = { title: string, subtitle: string, legend: Legend, crux: Segment[][], sections: Section[] }
Legend  = { [kind]: { label: string, blurb: string } }           // one entry per kind used
Section = { id: string, time: string, heading: string, summary: Segment[][], nodes: Node[] }
Node    = { kind: Kind, text: Segment[], zoom?: Segment[][], children?: Node[] }
Segment = string | Span
Span    = { t: string, kind: Kind, zoom: Segment[][], children?: Node[] }
Kind    = "tactic" | "lesson" | "mechanism" | "caveat" | "moment"
```

- `Segment[][]` is an array of paragraphs; each paragraph is an array of strings and Spans.
- A **Span** is a highlighted phrase inside running text. Clicking it opens a panel directly under that line showing its `zoom` paragraphs (which may contain Spans, so depth is recursive) and optional `children` nodes. Clicking again closes it.
- A **Node** is one line (8–25 words) with a colored kind marker. If it has `zoom` or `children` the line is clickable and opens a panel below it; otherwise it is plain.
- `time` is the source's own unit for the section start: a stream time (`"2:30"`), a page (`"p.14"`), a section (`"§3"`), a commit. Rendered in mono.
- `id` is a stable kebab-case slug, used for cross-references in prose ("see the security section") and by lens partitions.
- Node `text` is one sentence. `zoom` is 1–3 short paragraphs. `children` are sub-nuggets. Grandchildren are the floor.
- Plain ASCII quotes. No emoji. No markdown inside strings (the renderer sets `textContent`).

## Lens files

A lens pass writes `{ "sections": Section[] }` only. `build.py --lens <file>` appends those sections after the main ones. The lens index file is a reference object, not rendered:

```
{ "items": [ { "time": string, "location": string, "topic": string, "who": string, "one_line": string, "used_in": "<section id>/<first words of node text>" | "unused" } ] }
```

## Renderer contract (shell.html)

- Fragment, not a document: starts with `<title>`, then `<style>`, markup, `<script id="guide-data">`, app script. Artifact publish wraps it; `build.py --standalone` wraps it for a local file.
- Three-state theme: all tokens on bare `:root`, redefined under `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` and `:root[data-theme="dark"]`.
- Kind classes: `kind-tactic`, `kind-lesson`, `kind-caveat`, `kind-mechanism`, `kind-moment`. Tokens `--kind-<kind>`.
- Sections are disclosures; only the first opens by default. Spans and clickable node lines are keyboard-operable.
- No libraries. Google Fonts only (Bricolage Grotesque, IBM Plex Sans, IBM Plex Mono) with real fallbacks.
