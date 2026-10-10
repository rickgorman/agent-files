# decision-gui protocol

The contract between `references/deck.html` (the page) and `scripts/decision_gui.py` (the build tool and local server). Both sides implement exactly this. Change this file first if the contract changes.

## 1. Deck JSON

One file per deck, written by Claude. Write it to a scratch directory outside the user's repo, as `<slug>.deck.json`.

```json
{
  "id": "platform-2026-10",
  "title": "Platform decision deck",
  "storeKey": "platform-deck-v1",
  "decisions": [
    {
      "id": "F1",
      "group": "Data",
      "short": "Primary store",
      "q": "Which database holds the source of truth?",
      "why": ["Paragraph one.", "Paragraph two."],
      "warn": "WARNING: optional one-line risk.",
      "locked": "Locked 10-08",
      "options": [
        { "k": "A", "t": "Option title", "g": ["gain"], "c": ["cost"], "lean": true }
      ]
    },
    {
      "id": "S2",
      "group": "Style",
      "short": "Lint conflicts",
      "q": "Settle 3 lint conflicts",
      "why": ["..."],
      "sub": [ { "id": "C1", "t": "Shared test setup", "o": [["a", "Label", true], ["b", "Label"]] } ]
    }
  ]
}
```

Rules:
- `id`: unique, short. Shown as the prefix and used in the answer text.
- `short`: at most 17 characters. It is the answer-sheet label.
- `options`: 2 to 4 entries. Exactly one has `"lean": true`. `k` is an internal key; the page shows A / S / D / F by position.
- `sub`: replaces `options` for a page of small two-way choices. Each row has exactly two options (`a`, `b`); exactly one is the lean.
- `locked`: optional. The page preselects the lean and disables choosing.
- `storeKey`: optional. Defaults to `"decision-gui:" + id`. Only set it to keep progress from an older page.

## 2. Page boot

The page carries the deck inside the template:

```html
<script id="deck-data" type="application/json">/*DECK_JSON*/</script>
```

`decision_gui.py` replaces `/*DECK_JSON*/` with the deck JSON plus one injected field, `"mode"`:
- `"mode": "artifact"` from `build`. Voice controls are hidden. Answers live in the browser and in the copied text.
- `"mode": "local"` from `serve`. Voice works, and answers are also posted to the server.

The JSON is escaped for safe embedding: every `<` becomes `<`, and U+2028 and U+2029 are escaped too. The `<title>` tag gets `title` from the deck, HTML-escaped. The template's `<title>` must sit in the first 8 KB of the file.

## 3. Answer text (what Claude reads)

```
<title> (<answered> of <N> answered)

F1 = D · Postgres, with read replicas later (lean)
F2 = S · ... (not lean)
    note: free text from the note field
S2 = all leans: C1 A, C2 A, C3 A
S2 = C1 S (not lean), C2 A, C3 A
    C1 S: label of the chosen non-lean option

Open: F2, R4          (or "All answered.")
```

Letters are positional: A, S, D, F for options and A, S for sub rows.

## 4. Local server (mode "local")

Bind `127.0.0.1` only. The default port is 7317; if it is taken, try the next 20 ports. When ready, print exactly one line to stdout:

```
DECISION_GUI_URL http://127.0.0.1:<port>/
```

| Method | Path | Behavior |
|---|---|---|
| GET | `/` | The page, with the deck injected and `mode: "local"` |
| GET | `/api/health` | `{"ok": true, "engine": "<name or null>", "streaming": true|false}` |
| POST | `/api/answers` | Body `{"text": str, "state": object}`, at most 1 MB. Writes `<out>.answers.txt` and `<out>.answers.json` atomically, prints `ANSWERS_SAVED <txt path>`, and returns `{"ok": true, "path": "<txt path>"}` |
| GET | `/api/answers` | The last saved `{"text", "state"}`, or 404 |
| WS | `/stt` | Speech to text (section 5) |

`<out>` defaults to the deck path minus `.deck.json`.

**Origin check.** Reject any POST or WebSocket upgrade whose `Origin` header is not `http://127.0.0.1:<port>` or `http://localhost:<port>`. Respond 403. This stops other websites from writing answers or using the microphone pipeline.

## 5. Speech to text over WebSocket `/stt`

**Client to server:**
- Text `{"type": "start", "sampleRate": 16000}` begins an utterance.
- Binary frames: mono 16-bit signed little-endian PCM at 16 kHz, any frame size.
- Text `{"type": "stop"}` ends the utterance.
- One utterance at a time per connection. A new `start` discards any unfinished one.

**Server to client:**
- On connect: `{"type": "ready", "engine": "mlx-whisper large-v3-turbo", "streaming": true}`. With no engine available: `{"type": "ready", "engine": null, "streaming": false}`.
- `{"type": "partial", "text": "<full hypothesis so far>"}` replaces the utterance text. Local engines send it about every 0.6 s while audio arrives.
- `{"type": "delta", "text": "<next chunk>"}` appends to the utterance text. It is used by engines that stream tokens after `stop` (OpenRouter).
- `{"type": "final", "text": "<full text>"}` replaces the utterance text and ends the utterance. It is always sent once after `stop`, even when the text is empty.
- `{"type": "error", "message": "<plain words>"}` reports a failure. The utterance ends.

**Engine order:**
1. **Local, preferred.** `mlx-whisper` with `mlx-community/whisper-large-v3-turbo` (cached on this Mac). Language `en`, temperature 0, `condition_on_previous_text=False`. Warm the model at startup. Partials come from re-transcribing the growing buffer at most every 0.6 s, one decode at a time. Cap the buffer at 120 s.
2. **OpenRouter fallback**, only when no local engine loads. The key comes from `OPENROUTER_API_KEY`, or from `op read "$DECISION_GUI_OPENROUTER_OP_REF"` when that variable is set. Never log the key, and never send it to the page.
   - **Model:** list `https://openrouter.ai/api/v1/models`, keep the models whose `architecture.input_modalities` contains `"audio"`, and sort them by price, cheapest first.
   - **Privacy:** call `/api/v1/chat/completions` with `"stream": true` and `"provider": {"data_collection": "deny", "zdr": true}`, so only endpoints that do not train on the data and keep zero data serve the request. Send the utterance as a WAV `input_audio` part, with the instruction "Transcribe this audio verbatim. Output only the transcript."
   - **Retries:** if a model has no allowed endpoint, try the next cheapest model, up to 3.
   - **Streaming:** forward each content chunk as `delta`, then send `final`.
3. **None.** Answer `ready` with `engine: null`. The page then shows that voice is unavailable.

## 6. Keys (page)

| Key | Action |
|---|---|
| ↑ / ↓ | Select the previous or next choice. ↓ past the last choice moves focus to the note field, and ↑ in the note moves back. On a `sub` page, ↑ / ↓ move between rows. |
| ← / → | Previous or next page. In a non-empty note, these keys move the text cursor instead. |
| Enter | Next page. If nothing is chosen on this page, take Claude's lean first. In the note field, Enter goes to the next page without taking the lean. |
| Hold Space | Record voice into the note field (local mode only). Release to stop. It works when focus is not in a text field. Inside the note field, Space types a space. |
| Hold ⌥ | Show the shortcut badges. ⌥A / ⌥S / ⌥D / ⌥F choose an option; on a `sub` page they answer the highlighted row. |
