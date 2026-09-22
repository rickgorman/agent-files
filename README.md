![agent-files](world-map.png)

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

### [`/jev-review-loop`](skills/jev-review-loop/)

> *Your agent builds the rubric. Jev scores, the fixing agent repairs, Jev scores again.*

Review a codebase or diff with criteria derived from the project, or supply your
own rubrics. Jev selects applicable rules and grades current code; the fixing
agent works from that round's failures. The loop records coverage and spend and
stops on success, stalled progress, or its round and budget limits.

## Grok Bot

A separate steal path. [`grok-bot/`](grok-bot/) is fleet playbooks for Grok Bot, not Claude `skills/`. Copy a package onto the box:

```bash
gh repo clone rickgorman/agent-files
cp -R agent-files/grok-bot/<name> /home/box/agent-data/workflows/<name>
```

That is `/home/box/agent-data/workflows/`, not `~/.claude/skills/`. The section has its own hero on [`grok-bot/README.md`](grok-bot/) (`grok-bot-hero.png`). Each package folder has a hero too. The root banner stays `world-map.png` — do not stack a grok-bot image here.

### [`/fleet-spring-clean`](grok-bot/fleet-spring-clean/)

> *Declutter a multi-bot fleet: two Notion brains, one boss per seat, boards, briefs, arsenal.*

The sidebar filled up. Notion grew a third "misc" root. Skills got pasted into blurbs. This is a phased clean — inventory first — and the playbook stays free of your URLs.

## Table of Contents

- [Quick Start](#quick-start)
- [Grok Bot](#grok-bot)
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

Copy a Grok Bot package onto the box:

```bash
gh repo clone rickgorman/agent-files
cp -R agent-files/grok-bot/<name> /home/box/agent-data/workflows/<name>
```

Then enable it and invoke `/<name>` from Grok Bot. See [`grok-bot/`](grok-bot/).

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
