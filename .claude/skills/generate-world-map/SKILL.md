---
name: generate-world-map
description: >-
  Repaint the root README's world map from the skill registry: read
  .claude/data/skill-map.yaml, load the local Frontier Systems Cartography
  style guide, and emit one paste-ready ChatGPT prompt. Use after adding or
  removing a published skill, when the map is stale, or on
  /generate-world-map. The prompt stays in the session — never commit it.
---

# /generate-world-map

How to rebuild `world-map.png` — the single picture at the top of the root
README showing every published skill as one place on one frontier. Same style
system as [generate-hero.md](../../data/generate-hero.md): JoyRudder's unpublished
Frontier Systems Cartography guide, loaded from the local checkout, never
copied into this repo.

The generator is **ChatGPT**. This harness does not emit the canvas. Your job
is a paste-ready prompt **in this session, to the human**. The PNG lands when
they drop it in.

Never put the prompt on a PR, in a commit, or in any published surface. The
prompt is a trade secret. That includes this map's prompt, which is longer and
more valuable than a hero's.

## Regenerate when the roster changes

The map is a function of one file:
[`skill-map.yaml`](../../data/skill-map.yaml). A skill
added to `skills/` without an entry there is a skill that vanishes from the map
on the next regeneration. `/add-new-skill` writes the entry; this file turns
entries into a picture.

Regenerate when: a skill is added or removed, a skill's region or placement
changes, a route changes, or a background landmark changes. Do not regenerate for a wording tweak inside a
skill — the map costs a human round-trip.

## Find the style guide

Identical to the hero procedure. The guide is `skills/image-prompt/SKILL.md`
inside a repo named exactly `joyrudder`.

```bash
guide="$HOME/work/joyrudder/skills/image-prompt/SKILL.md"
if [ ! -f "$guide" ]; then
  d=$(find "$HOME/work" -maxdepth 2 -type d -name joyrudder -print -quit 2>/dev/null)
  guide="${d:+$d/skills/image-prompt/SKILL.md}"
fi
if [ -f "$guide" ]; then echo "$guide"; else echo "missing: local joyrudder style guide" >&2; exit 1; fi
```

Read it in full. That file is the style. If it is missing, **stop** — do not
invent a substitute, and do not read `~/.claude/skills/image-prompt`, which can
drift.

## Read the registry

```bash
cat .claude/data/skill-map.yaml
node_count=$(grep -c '^  - name:' .claude/data/skill-map.yaml)
region_count=$(grep -c '^  - key:' .claude/data/skill-map.yaml)
edge_count=$(grep -c '^      - to:' .claude/data/skill-map.yaml)
echo "$node_count nodes / $region_count regions / $edge_count edges"
```

Cross-check against `ls skills/`. A folder with no entry, or an entry with no
folder, is a bug — say so and stop rather than drawing a map you know is wrong.

Drop any region no skill claims. Regions are scaffolding for the roster, not
decoration.

### Locations and route DAG

The registry separates three kinds of information:

- `regions[].ground`, `skills[].placement`, and `landmarks[].placement` describe
  geography. Honor explicit placement constraints while composing the scene.
- `skills[].edges` defines the directed inter-site work routes. Validate that
  every target exists, that there are no duplicate edges or cycles, and that
  the route covers every skill. Derive travel order from these edges, not YAML
  listing order or the arrangement in an old image. This is a map of work
  routes, not a claim that the skills require each other at runtime.
- Each site's `transform` and `terminates` describe its internal mechanism,
  including local review loops. Those loops do not become edges in the DAG.

Derive roots, junctions, and the terminal site from the current registry. The
reading tributaries converge at dag-reader; the relay continues through the
other regions and ends at handoff-beads. Jev is immediately upstream of
screen-flow, with no intervening site. Do not force branches into a made-up
linear sequence or require a single entry skill when the DAG has several roots.

Background `landmarks` are separate from the skill roster and route DAG. Keep
their placements and signs, but do not turn them into processing stages or add
individual Grok Bot packages to the skill registry.

## Pick the canvas

Use `canvas.primary` from the registry: **2172×724**, exactly **3:1**. Put these
exact dimensions at the start of the image-generation prompt. Both
`world-map.png` and `agent-files-hero.png` use this size.

Do not substitute another canvas based on skill count. If the roster cannot
fit legibly, simplify the mechanisms or propose splitting the map before
changing the registered dimensions. Do not shrink labels to fit more sites.

## Compute the type floor

Root README displays at about **900px** wide. The image file stays at
**2172×724**; calculate lettering for the smaller display width.

Per the style guide, `min_file_px = ceil(10 × gen_width / display_width)`.

The mathematical floor is `ceil(10 × 2172 / 900) = 25px`. Use the stronger
registry minimum of **28px** and a title around **140px**. Put both design
sizes in the prompt. A label that cannot clear the floor gets cut, not shrunk.
Enlarge signs rather than compressing text. Keep the PNG at its native size.

## Attach references

Attach, in this order:

1. The current `world-map.png` **and** `agent-files-hero.png` if both exist —
   composition and style. Say they are references for landscape, light, border,
   and cartouche — **not** layouts to clone. Without that sentence the
   generator copies the old regions.
2. Each published skill's `*-hero.png`. These are **mechanism** references:
   understand the machine, then **simplify it to map-scale**. One distinctive
   silhouette, one slash-prefixed sign. Do **not** paste miniature skill heroes
   into the map. Do not reproduce a standalone hero at full complexity.

## Landmark placement

Compose one canyon / plateau world, not four boxes. Put landmarks at
**different elevations** (ridge, plateau, trestle, lower yard) with a generous
scenic opening through the middle distance. Integrate them into cliffs and
bridges. Do not arrange equal rectangular panels. Keep every skill identifiable
without zooming.

When adding a skill later: give it one distinctive physical mechanism, one
readable silhouette, and one slash-prefixed sign. **Rebalance the whole
landscape** instead of squeezing in another inset or shrinking existing labels.

## Label budget

Five label classes, and the viewer must feel the difference before consciously
reading a word. Permitted words, and nothing else:

- One title cartouche: the registry's `title`. **No subtitle.** Largest.
- One giant uppercase banner per drawn region: the region's `banner`
- One plaque per skill: the skill's `plaque`, verbatim, slash prefix included.
  All skill plaques comparable in size and importance.
- Local mechanism plates **only** when the registry's `structure:` named them
  (example: `NAV`, `SHOT`, `FLOW` on the `/screen-flow` gallery). Smaller than
  plaques, still ≥ the type floor.
- Background landmark signs from `landmarks[].plaque` only (currently
  `Grok Bot Mountain`). Subordinate to region banners and skill plaques, but
  still above the type floor. They do not label a skill or processing stage.

That is the whole list. Spell it out in the prompt as an exhaustive one, then
ban the rest by name — the generator will otherwise invent them:

> No SOURCE, CRUX, edge verbs, subtitle, legend, caption, annotation, numbered
> stage, statistic, fake body copy, tiny writing on papers, signage on tents,
> decorative pseudo-text, letter-like marks, or logos. If an object would
> normally carry writing, leave it blank or use non-letter decorative texture.

Edge verbs are gone on purpose. A route between two sites is drawn as a route;
naming it costs a label and buys nothing at 900px. Same for the artifact's
before/after names — the registry's `transform:` tells that story
architecturally, through the shape of the building, not with words.

No "System At A Glance" stats box. The roster numbers are small type by
construction and die at 900px display — they belong in README prose, where they
are also correct without a repaint.

## Contrast

The default parchment-on-parchment map reads as mush at README width. Force
separation:

- The title, every region banner, and every skill plaque are **bright cream**
  and are the **lightest values in the frame**. Nothing in the landscape may be
  as bright as a sign.
- Near-black lettering, hard dark borders, real cast shadows.
- Push the landscape **down in value and saturation**: deep shaded pine on the
  ridge, muted ochre plateau, cool mid-tone gray-brown stone, honey timber,
  brass, copper, sepia, umber, muted olive, rust red. Clear golden daylight,
  open atmosphere, strong depth — not muddy, not monochrome, not dust-bowl.
- Keep open ground between adjacent sites. No site touches another's plaque.
- The blue trunk is the only saturated cool value and stays clear of plaque
  edges so it never fights the lettering.

## Write the prompt

Follow the style guide's assembly order, with the registry supplying the
subject material:

- Subject: the registry's `title` — the published skill roster as one frontier
- Kind: `map` — elevated scenic viewpoint, like a richly illustrated antique
  world map. Not an overhead map, isometric diagram, or flat flowchart. One
  continuous world inside an ornate carved wooden border.
- Size: exactly **2172×724**, **3:1**, as recorded in `canvas.primary`.
- Topology: **relay along one trunk**, with only the tributaries specified by
  the registry. A single source may fork through entry sites and converge at
  a junction; derive that arrangement from the DAG. Follow its directed edges
  to the terminal site. Honor `blue.leaves`: when the final artifact is retained
  in the handoff lattice, do not draw another scroll exiting beyond it. Each
  edge is a visible route, drawn not named. Honor explicit placement, especially
  Jev immediately before screen-flow. Regions must accommodate these routes.
- Per skill: `structure:` is what stands there, `transform:` is what the blue
  does passing through, `plaque:` is the sign bolted to it. State explicitly
  that a skill sits **inside its own region** and nowhere else, and that a
  plaque labels the **whole worksite**, not one building within it — the
  generator drifts on both.
- Blue: the registry's `blue:` block, one continuous route, brightest where it
  exits.
- Background landmarks: use their registered placements, structures, and signs;
  keep them visually subordinate and off the work route.
- Termination: only where a skill's entry has a `terminates:` line.
- Composition: five or six large visual masses with generous open ground.
  Say that empty land, water, and sky are intentional, or the generator fills
  every inch.
- Detail budget: ornament on the border, the cartouche, the banners, the
  plaques, major entrances, and the one central mechanism. Large readable
  planes elsewhere. No gear fields, rivets, rubble, crowds, tangled rails.

Close with the exclusions the style guide requires, plus the named ban list
from the label budget above.

Emit **one paste-ready prompt** in a fenced `text` block. Do not generate with
this harness's image tool. ChatGPT is the generator.

Outside the fence, one line: kind, dimensions, aspect ratio, exact permitted
on-image words, and where to save the PNG (`world-map.png` at the repo root).

## After the PNG lands

Use the newly supplied `~/Downloads/world-map.png` or
`~/Downloads/agent-files-hero.png`; if both exist, use the user's identified
image or the newer matching image after inspection, not a stale namesake.
Verify it is **2172×724**, then copy it unchanged to **both** `world-map.png`
and `agent-files-hero.png` at the repo root. Keep the two files byte-identical.
If the dimensions differ, report the mismatch instead of silently resizing.

Root README line 1 is the only embed:

```markdown
![agent-files](world-map.png)
```

The map is the root README's picture. Per-skill heroes stay in their own skill
READMEs; do not stack a hero on the root page.
