# Plat seed for a screen-flow board

Copy `examples/basic` from [zackham/plat](https://github.com/zackham/plat), or a Vite app with `plat` from `github:zackham/plat`. Put viewport PNGs in `public/shots/`. Replace `src/seed.ts` with a document in this shape, then `import { settleDoc } from "plat"`.

## Type

| Node | `fontSize` | box |
| --- | --- | --- |
| Board title | 36 | wide enough not to clip; ~80px tall |
| Subtitle | 22 | color `#5d6b82` |
| Step caption | 22 | same width as the shot, ~72px tall |
| Fail caption | 22 | color `#bd3434` |
| Pass caption | 22 | color `#19724d` |

## Layout

One outer `group` with `layout.dir: "v"` so title and lanes stack. Each lane is a `frame` (`layout.dir: "h"`) whose children are vertical `group`s (shot over caption). Then `nodes = settleDoc(nodes)`.

Shot `w`/`h` **must match the screenshot aspect**. Mobile: `390×844`. plat stretches `src` to the box.

```ts
import { settleDoc } from "plat"
import type { AnyNode, PlatDoc } from "plat"

const SHOT_W = 390
const SHOT_H = 844

export function seedDoc(): PlatDoc {
  const nodes: AnyNode[] = [
    {
      id: "board",
      type: "group",
      x: 0, y: 0, w: 0, h: 0, index: "a0",
      layout: {
        dir: "v", gap: 48,
        padding: { t: 48, r: 48, b: 48, l: 48 },
        justify: "start", align: "start",
        sizing: { main: "hug", cross: "hug" },
      },
    },
    {
      id: "title", type: "text", x: 0, y: 0, w: 1600, h: 80,
      index: "000000", parentId: "board",
      text: "Login verify: unfixed develop vs verify-time Buyer",
      fontSize: 36,
    },
    {
      id: "sub", type: "text", x: 0, y: 0, w: 1600, h: 56,
      index: "000001", parentId: "board",
      text: "Same clicks. Viewport screenshots, toasts intact. ⌘/Ctrl + scroll zooms.",
      fontSize: 22, color: "#5d6b82",
    },
    {
      id: "lane-before", type: "frame", name: "Before — login verify on unfixed develop",
      x: 0, y: 0, w: 0, h: 0, index: "000002", parentId: "board",
      layout: {
        dir: "h", gap: 32,
        padding: { t: 24, r: 24, b: 24, l: 24 },
        justify: "start", align: "start",
        sizing: { main: "hug", cross: "hug" },
      },
    },
    {
      id: "b1", type: "group", x: 0, y: 0, w: 0, h: 0,
      index: "000000", parentId: "lane-before",
      layout: {
        dir: "v", gap: 12,
        padding: { t: 0, r: 0, b: 0, l: 0 },
        justify: "start", align: "center",
        sizing: { main: "hug", cross: "hug" },
      },
    },
    {
      id: "b1-shot", type: "image", x: 0, y: 0, w: SHOT_W, h: SHOT_H,
      index: "000000", parentId: "b1",
      src: "/shots/before-01.png",
    },
    {
      id: "b1-cap", type: "text", x: 0, y: 0, w: SHOT_W, h: 72,
      index: "000001", parentId: "b1",
      text: "1. Signup — POST /users 201",
      fontSize: 22,
    },
    // …more steps, then a second frame for After
  ]
  return { format: "plat", version: 1, nodes: settleDoc(nodes) }
}
```

Repeat the step group for each shot. Add a second `frame` sibling of `lane-before` for the next variant. Fail/success last-step captions use the red/green colors above and mention the proving request (`PATCH /buyers/-1 → 404`).

## Host

Keep `examples/basic` `host.ts` (localStorage + `uploadAsset` as data URLs). Point `loadDoc` at `seedDoc()` so a Reset restores the filmed board. Serve with `npm run dev -- --host 127.0.0.1 --port 41327`.

## Zoom

Do not reimplement zoom. plat's canvas already maps ⌘/Ctrl + wheel to `zoomToward`. After serve, confirm that gesture once.
