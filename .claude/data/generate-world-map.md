# Generate the root world map

How to rebuild `world-map.png` — the single picture at the top of the root
README showing every published skill as one place on one frontier. Same style
system as [generate-hero.md](generate-hero.md): JoyRudder's unpublished
Frontier Systems Cartography guide, loaded from the local checkout, never
copied into this repo.

The generator is **ChatGPT**. This harness does not emit the canvas. Your job
is a paste-ready prompt **in this session, to the human**. The PNG lands when
they drop it in.

Never put the prompt on a PR, in a commit, or in any published surface. The
prompt is a trade secret. That includes this map's prompt, which is longer and
more valuable than a hero's.

## Regenerate when the roster changes

The map is a function of one file: [`skill-map.yaml`](skill-map.yaml). A skill
added to `skills/` without an entry there is a skill that vanishes from the map
on the next regeneration. `/add-new-skill` writes the entry; this file turns
entries into a picture.

Regenerate when: a skill is added or removed, a skill's region changes, or an
edge between skills appears. Do not regenerate for a wording tweak inside a
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

## Pick the canvas

| Skill count | Canvas | Ratio |
| --- | --- | --- |
| 1–10 | **1200×500** | 24:10 |
| 11–18 | 1440×960 | 3:2 |
| 19+ | stop — split the map or cut the roster |

24:10 is the default and what `world-map.png` is. Past ten sites the wide strip
starves each site of area and the plaques fall under the type floor; take the
vertical room instead. Do not shrink the type to fit more sites.

## Compute the type floor

Root README displays at about **900px** wide, and the map is rendered at
**1×** that slot — not doubled for HiDPI. It stays slightly soft on a retina
screen; that is the accepted trade, and the registry's `render_scale` records
it. Rendering at 2× would halve the effective type floor against the slot and
the label hierarchy stops being the design.

Per the style guide, `min_file_px = ceil(10 × gen_width / display_width)`.

| Canvas | Floor in file | Title in file |
| --- | --- | --- |
| 1200×500 | **14px** | ~80px |
| 1440×960 | **16px** | ~96px |

Both numbers go in the prompt. A label that cannot clear the floor gets cut,
not shrunk.

## Attach a style reference

Attach the current `world-map.png` (or, on a first run, the JoyRudder frontier
map the style came from) to the ChatGPT message and say in the prompt that it
is a **style reference only** — carved wood, parchment cartouches, frontier
landscape, old-world systems-map storytelling — and that its exact layout and
labels must not be copied. Without that sentence the generator reproduces the
reference's regions.

## Label budget

Two label classes, per the registry's `label_system` block, and the viewer must
feel the difference before consciously reading a word. Permitted words, and
nothing else:

- One title cartouche: the registry's `title`. **No subtitle.**
- One giant banner per drawn region: the region's `banner`
- One plaque per skill: the skill's `plaque`, verbatim, slash prefix included

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
- Kind: `map` — pseudo-isometric top-down story map, viewed slightly from
  above, one continuous world inside an ornate carved wooden border
- Size: from the canvas table above
- Topology: **relay along one trunk**. The blue enters as raw work at the
  lower left, passes through each skill site in region order, and leaves at the
  right edge. Each `edges:` entry is a visible route, drawn not named.
- Per skill: `structure:` is what stands there, `transform:` is what the blue
  does passing through, `plaque:` is the sign bolted to it. State explicitly
  that a skill sits **inside its own region** and nowhere else, and that a
  plaque labels the **whole worksite**, not one building within it — the
  generator drifts on both.
- Blue: the registry's `blue:` block, one continuous route, brightest where it
  exits.
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

Save as `world-map.png` at the repo root. ChatGPT returns whatever it returns —
do not rescale it to the nominal canvas.

Root README line 1 is the only embed:

```markdown
![agent-files](world-map.png)
```

The map is the root README's picture. Per-skill heroes stay in their own skill
READMEs; do not stack a hero on the root page.
