---
name: screen-flow-plat
description: >-
  Drive a real browser through a multi-screen product flow, capture viewport
  screenshots with toasts intact, and compile them onto a plat canvas of
  titled, bounded lanes. Use when the user wants to visualize a flow, filmstrip
  a journey, compare before/after screens, or build a plat of onboarding,
  checkout, or login. Invoke as /screen-flow-plat [flow description].
---

# /screen-flow-plat

Turn a multi-screen product flow into a plat board of **real screenshots**, not schematic phones. Drive the browser, wait for toasts, crop to the viewport, drop each shot into a titled lane, annotate at screen-reading type, and serve a canvas where **⌘/Ctrl + scroll zooms**.

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot).

## Input

Parse:

1. **Flow** — the screens and the story (one path, or named lanes such as before/after, happy/fail). May be the rest of the argument, or the flow already in this conversation (UAT, a bug, a PR).
2. **`--url <base>`** — app origin. If omitted, detect a running local app; else ask.
3. **`--viewport mobile|desktop`** — default `mobile` (390×844, deviceScaleFactor 2). Desktop is 1440×900.
4. **Empty** — if this conversation already has a flow and shots, reuse them. Otherwise ask what to film. Do not pick a random route from the repo.

One board per run. Multiple variants of the same story are lanes on that board, not extra boards.

## Constants

Use these at 100% zoom. Do not shrink them to “fit more phones.”

| Role | `fontSize` |
| --- | --- |
| Board title | 36 |
| Lane / step caption | 22 |
| Annotation / callout | 22 |

Never put body type on the canvas below 18. The previous HTML board used 11px captions — that is the failure this skill exists to prevent.

Shot display size equals the CSS viewport (mobile 390×844, desktop 1440×900). plat **stretches** images to `w`×`h`; set those to the screenshot aspect.

## Procedure

1. **Name the lanes and steps.** A lane is one bounded flow (example: “Before — login verify”, “After — verify-time Buyer”). A step is one screen. Write a one-line title for the board that says what differs across lanes.

2. **Ensure plat.** Prefer an existing clone of [zackham/plat](https://github.com/zackham/plat). If none, `git clone https://github.com/zackham/plat`. Do not reinvent a custom HTML board. plat already implements ⌘/Ctrl + wheel zoom toward the cursor (`Plat.tsx` wheel handler). A hand-rolled board is a last resort, and only if it implements the same zoom.

3. **Scaffold the host** in a dedicated run directory (not the product repo unless asked): copy `examples/basic` from plat, or a Vite app that depends on `plat` (`npm i github:zackham/plat`). Put screenshots in `public/shots/`. Seed the document from `references/plat-seed.md`.

4. **Drive the browser.** Playwright, system Chrome (`channel: "chrome"`). Headed. Viewport from the flag. `waitUntil: "domcontentloaded"` — never `networkidle` on apps that poll. For each step: perform the user action, **wait until the toast/alert/error is visible**, then screenshot **the viewport** (`fullPage: false`). If a toast sits at the bottom, it must still be in the PNG. Do not reconstruct screens in HTML/SVG.

5. **Reuse shots** when this conversation already captured them. Re-crop to the CSS viewport (device pixels = CSS × deviceScaleFactor) from the edge that keeps the toast.

6. **Compile the plat.** One outer auto-layout group, vertical: title, subtitle, then one `frame` per lane. Each frame is a horizontal row of step columns (image over caption). Call `settleDoc`. Frame `name` is the lane title. Captions are 22px and include the proving request when you have it (`PATCH /buyers/-1 → 404`). Fail/success lanes get distinct caption color (`#bd3434` / `#19724d`).

7. **Serve and verify.** `npm run dev` on a free port (41327 if free). Open the URL. Confirm: title readable at fit-zoom, captions ≥ 22, ⌘/Ctrl + scroll zooms, each lane is a bounded framed section, toasts visible in the shots. Tell the user to hard-refresh if an older board is cached.

## Output

Report, in this order:

1. **URL** — the running board.
2. **Title** — as on the canvas.
3. **Lanes** — name, step count, what the last shot proves.
4. **Type** — title 36 / captions 22, and that ⌘-scroll zoom is live.
5. **Shots directory** — where the PNGs live.

## Guardrails

- Real screenshots only. No schematic phones, no SVG reconstructions of product UI.
- Capture after the toast exists. Viewport shot, not a full-page crop that drops the overlay.
- Do not edit the product app to make filming easier unless the user asked for a product change.
- Do not commit the board or shots into the product repo unless asked.
- Do not skip plat for a custom HTML board except as a last resort, and then ⌘-scroll zoom is mandatory.
- Do not use caption `fontSize` under 18.
