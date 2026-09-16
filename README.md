![agent-files](world-map.png)

# agent-files

Skills I actually run.

## The Prompts

### [`/refine-plan`](skills/refine-plan/)

> *Four critics map-reduce a markdown plan in place until yield is zero.*

A first-draft plan is cheap. Building the wrong one is not. Four model families critique the file concurrently; the session reduces and scores yield. Wording nits don't count. It stops when yield is zero.

### [`/dag-reader`](skills/dag-reader/)

> *Read a source into a thesis–claim–fact DAG and prune it to one crux paragraph.*

A summary flattens an argument. This keeps the spine: theses, the claims that hold them up, and the facts those claims rest on. It prunes to the Pareto leaves and ends with one paragraph that is the crux.

### [`/dev-manager`](skills/dev-manager/)

> *The orchestrator judges; coder lanes emit by a fixed task→model fallback sequence.*

The session model that writes the code also judges the code. This splits that: you stay the orchestrator, and every implementation line lands on a coder lane picked from a locked fallback table, not vibes.

### [`/screen-flow`](skills/screen-flow/)

> *Drive a browser through a product flow and compile viewport screenshots onto a plat of titled lanes.*

A flow explanation that *describes* screens is easy to misread. This films the real product: clicks, toasts intact, laid onto a plat canvas. Schematics are a bug, not a fallback.

### [`/expandable-reader`](skills/expandable-reader/)

> *One page: a world-map paragraph, toggle sections, phrases that open in place.*

A summary gives everyone the same two minutes. This reads the whole source, distills it into typed nuggets (tactic, lesson, mechanism, caveat, moment), and renders a drill-down page so a reader with any amount of time gets the map first and picks where to go deeper.

## Table of Contents

- [Quick Start](#quick-start)
- [Design Philosophy](#design-philosophy)
- [License](#license)

## Quick Start

Copy a skill folder into Claude Code:

```bash
gh repo clone rickgorman/agent-files
cp -R agent-files/skills/<name> ~/.claude/skills/<name>
# or into a project:  cp -R agent-files/skills/<name> .claude/skills/<name>
```

Then invoke `/<name>`.

## Design Philosophy

Pretty simple.

### 1. Share tools I use all the time

If I don't run it, it doesn't ship.

### 2. Scale with how smart the models get

Build tools that get better as the models get smarter, not ones that fight the next generation.

### 3. Single-purpose and composable

Each skill does one job. Stack them; don't merge them into a kitchen sink.

## License

MIT. See [LICENSE](LICENSE).
