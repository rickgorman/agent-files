---
name: decision-gui
description: >-
  Turn a batch of pending human decisions into a one-screen decision deck: one
  page per decision with framing, 2–4 choices with gains and costs, and your
  lean, plus keyboard navigation, hold-Space voice notes through local Whisper,
  and an answer sheet you read back. Use whenever more than 8 decisions are
  waiting on the human in an interactive session, when a decision list in chat
  has grown too long to answer, or when the user runs /decision-gui. With 8 or
  fewer, ask in chat instead. Invoke as /decision-gui [DECK.json] [--artifact].
---

# /decision-gui

Nine or more decisions in one chat message are hard to read and hard to answer. The human skims, answers half, and loses the rest. This run puts each decision on its own page, shows your honest lean, lets the human answer by keyboard or voice, and hands the answers back in a fixed text format you parse.

Files in this skill folder. `<skill-dir>` below is where it is installed: `~/.claude/skills/decision-gui`, or `.claude/skills/decision-gui` in a project.
- `references/protocol.md`: the deck JSON format, the answer text format, the local server API, the speech protocol, and the keys. Read it before you write a deck.
- `references/deck.html`: the page template. It holds no content; the deck JSON fills it.
- `scripts/decision_gui.py`: `serve` runs the page locally with voice. `build` writes a self-contained HTML file.

## Input

Arguments: `$ARGUMENTS` (or `{{args}}` — same slot, whichever the harness interpolates).

Parse:

1. **A path to a `.deck.json`** — serve that deck. Use it to reopen a deck the human has not finished.
2. **`--artifact`** — build a self-contained page instead of serving. Use it when the human wants the deck on another device, or the local server cannot run.
3. **`--no-voice`** — serve without a speech engine.
4. **Empty** — collect the decisions that are pending in this conversation. If there are 8 or fewer, ask them in chat and stop. If there are none, say so and stop. Do not invent decisions to fill a deck.

One deck per run.

## Constants

- Threshold: more than 8 pending decisions.
- Options per page: 2 to 4. Exactly one lean.
- `short` label: 17 characters or fewer.
- Default port: 7317, then the next 20.

## Procedure

### 1. Write the deck JSON

Write `<slug>.deck.json` in a scratch directory outside the user's repo. The format is in `references/protocol.md` §1. Quality rules:

- **One real decision per page.** Merge choices that cannot be made separately. Split a page that hides two decisions. Small two-way choices that share one context go on one page as `sub` rows, for example a lint config's internal conflicts.
- **Order pages by dependency,** then by group. If decision B depends on the answer to A, put A first and say so in B's `why`.
- **`q` is the question the human answers,** in their words, not the system's.
- **`why` is 1–2 short paragraphs:** the problem, and the facts that decide it. Put numbers and evidence here. Add `warn` for a real risk; it starts with `WARNING:` or `CAUTION:`.
- **Each option gets 1–3 gains (`g`) and 1–3 costs (`c`).** Every option needs at least one cost, your lean included. Keep each bullet under about 70 characters.
- **The lean is your honest recommendation.** Do not lean toward the option that is easiest for you.
- **Decisions already made** can appear as `locked` pages, so the deck matches the count you gave the human.
- Plain, short sentences. No filler.

Validate before going on: unique ids, exactly one lean per page, `short` lengths, and a cost on every option.

### 2. Serve it (default: local, with voice)

Run in the background:

```bash
uv run --script <skill-dir>/scripts/decision_gui.py serve <deck.json>
```

Read the `DECISION_GUI_URL …` line from its output. Give the human that link in one line, with the keys:
- ↑ / ↓ choose, ← / → change page, Enter goes next (and takes the lean if nothing is chosen).
- Hold Space to dictate a note.
- Hold ⌥ to see every shortcut.

Do not open the URL yourself; the human clicks it.

The server saves answers as the human works, to `<deck path minus .deck.json>.answers.txt`, and prints `ANSWERS_SAVED <path>` on each save.

**Voice** uses local Whisper (`mlx-whisper`, large-v3-turbo, Apple Silicon) and streams partial text while the human speaks. If no local engine loads, the server falls back to OpenRouter:
- The key comes from `OPENROUTER_API_KEY`, or from `op read "$DECISION_GUI_OPENROUTER_OP_REF"` (1Password CLI) when that variable is set.
- It uses the cheapest audio-capable model, and only endpoints that do not train on the data and retain none.

With no engine at all, the page still works and shows voice as unavailable.

### 3. Fallback: a self-contained page (no voice)

With `--artifact`, or when the server cannot run:

```bash
python3 <skill-dir>/scripts/decision_gui.py build <deck.json>
```

It needs only the Python standard library. If your harness can publish an artifact, publish the HTML file it prints. Otherwise hand the human the file path. Voice is hidden in this mode; the human copies the answer sheet back into chat.

### 4. Read the answers and act

When the human says they are done, or pastes the sheet:

1. Read `<deck>.answers.txt`. Pasted text wins if both exist.
2. Parse it with `references/protocol.md` §3. `OPEN` lines are still undecided.
3. Treat each note as the human's own instruction for that decision. Voice notes are transcribed speech, so read them for intent, not exact wording.
4. Stop the background server.

## Output

1. **The deck link** (or file path), with the keys, in one short message.
2. **After the answers come back:** a short table of id, choice, lean or not, and the note if any. Then call out every non-lean choice and every note that changes your plan, and list what is still `OPEN`.
3. **The decisions recorded** where the project keeps them (a decision log, an ADR, or the plan file), if the project has such a place.

## Guardrails

- Do not use the deck for 8 or fewer decisions unless the human asked for it.
- Never put secrets or private data in a `--artifact` page. The local server binds `127.0.0.1` only and rejects requests from any other origin.
- Do not reuse a `storeKey` across different decks. It exists only to keep progress on a rebuilt version of the same deck.
- If the human changes a decision later in chat, the chat wins. Update the record.
- Edit nothing in the repo except the decision record named in Output.
