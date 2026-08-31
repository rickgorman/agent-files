---
name: dag-reader
description: Read a source into a thesis–claim–fact DAG, prune to Pareto leaves, and end with one crux paragraph. Use when you need the load-bearing spine of an article, paper, report, transcript, or plan — not a summary. Invoke as /dag-reader <path|url|pasted text>.
---

# /dag-reader

Read a source. Build a DAG of its thesis(es) as they connect to their claim(s) as those claims are supported by fact(s). Prune to the Pareto frontier. End with one paragraph that is the crux of the article, synthesized from that DAG.

Source is `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates) if given (file path, URL, or pasted text). Otherwise use the article, paper, report, or transcript already in this conversation. Domain-agnostic: any argumentative or evidence-bearing text.

Do not write a file unless asked.

## Input

Parse the invocation:

1. **File path** — an existing local path. `Read` it in full.
2. **URL** — `http://` or `https://`. Fetch the page and use the article body, not the chrome.
3. **Pasted text** — the argument is itself the source.
4. **Empty** — use the argumentative source already in this conversation. If there isn't one, ask. Do not pick a random file from the repo.

If several sources are in play, ask which one. One source per run.

## Build

1. **Read the source in full before extracting nodes.** Do not sketch the DAG from the title, abstract, or first section.

2. **Extract a DAG: theses → claims → facts.** Render it like a tree (one spanning parent per node) plus cross-edges for the extra support links.

   - A **thesis** is a load-bearing conclusion the source is arguing, not a section heading.
   - A **claim** is a reason the thesis holds.
   - A **fact** is evidence, result, or cited state of the world the claim rests on.
   - Prefer what the source actually argues over what a reader might wish it argued. Do not invent a thesis the source does not argue.

3. **Cull** to the top **3 theses**, top **4 claims per thesis**, and top **3 facts per claim**. "Top" means most load-bearing for the argument (causal confidence, magnitude, directness) — not first-mentioned, not most colorful.

4. You may add **1–2 other node types** (examples: caveat, mechanism, warrant, implication). Extra types together may be **no more than 30%** of the DAG. Extra-type fraction = extra nodes / all nodes. If a candidate extra would break the cap, don't add it; the three core types already carry the argument.

### Tags

Stable tags so the tree, cross-edges, and crux can point at the same nodes:

| kind | tag | hangs off |
| --- | --- | --- |
| thesis | `T{n}` | root |
| claim | `C{n}.{m}` | thesis `T{n}` |
| fact | `F{n}.{m}.{k}` | claim `C{n}.{m}` |
| extra (caveat, mechanism, …) | one short tag + index, e.g. `V1`, `M1` | the node it qualifies |

`n` is 1–3, `m` is 1–4, `k` is 1–3 after cull. Keep tags stable through the prune; dropped nodes disappear, surviving tags do not get renumbered.

## Prune

5. **Remove weak leaf nodes first.**
6. **Check whether the source contained stronger nodes that were omitted.** If it did, add them in. Then continue the prune; do not grow the DAG for completeness.
7. **Then walk the whole tree the same way, recursively up the chain,** until only **Pareto-optimal leaf nodes** remain. After a layer is Pareto, the parents become the new leaves. Repeat until a pass drops nothing.

**Dominance:** drop a node if a sibling is easier-or-equal **and** stronger-or-equal on causal confidence, magnitude, and directness, and the dropped node does no unique inferential work. A remaining leaf must do inferential work no sibling also does.

Keep a node that is harder to establish if it is the only one doing some piece of work. Drop a strong node whose sibling already does the same work more directly.

Present only the stronger tree. Do not show the pre-prune DAG.

## Output

Use these five sections, in this order. No others.

1. **Legend** — tag, kind, role for every node type used. One line each. Include extra types only if they appear.

2. **Census** — counts by type and extra-type fraction of the DAG (extra / all, as a percentage). If extra types are 0, say `extra-type fraction: 0%`.

3. **Tree** — ASCII/box-drawing tree with typed nodes. Spanning parent only; extra support belongs in Cross-edges.

   ```
   T1  …
   ├── C1.1  …
   │   ├── F1.1.1  …
   │   └── F1.1.2  …
   └── C1.2  …
   T2  …
   └── C2.1  …
       └── F2.1.1  …
   ```

4. **Cross-edges** — links that make it a DAG rather than only a tree, each with a one-line why (`F1.2.1 → C2.1 — …`). If there are none, say `none`.

5. **Crux** — exactly one paragraph after the tree, synthesized from the surviving DAG. Pack as much of the article's actual crux as the frontier can carry: the theses, the load-bearing claims, and the facts that make them hold. Do not reintroduce pruned interior points except where a surviving node is itself about what does *not* hold. No second paragraph, no bullet restatement, no preamble ("In summary").

## Guardrails

- Do not write a file unless asked. The run's artifact is the five sections in the conversation.
- Do not summarize the source in parallel with the DAG. The tree plus the crux *is* the reading.
- Do not invent nodes to fill the cull caps. A thin source yields a thin DAG; say so in the census if the caps were not reached because the source had nothing more load-bearing.
- Do not skip the read-in-full step for a long source. A DAG from the abstract is a summary wearing a tree costume.
- Edit nothing in the repo. This skill reads.
