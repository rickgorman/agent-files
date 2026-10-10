#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "aiohttp",
#     "numpy",
#     "mlx-whisper; sys_platform == 'darwin' and platform_machine == 'arm64'",
# ]
# ///
"""Build or serve a decision-gui deck.

    python3 decision_gui.py build DECK.json [--out FILE.html] [--template PATH]
    uv run --script decision_gui.py serve DECK.json [--port 7317] [--out PREFIX] [--no-voice] [--template PATH]

The contract with references/deck.html is references/protocol.md. `build` uses the
standard library only; `serve` imports aiohttp, numpy and mlx-whisper late.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import contextlib
import functools
import html
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import wave
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn

if TYPE_CHECKING:
    import aiohttp
    import numpy as np
    from aiohttp import web

PLACEHOLDER = "/*DECK_JSON*/"
TITLE_SCAN_CHARS = 8192  # protocol: the template's <title> sits in the first 8 KB
TITLE_RE = re.compile(r"<title>.*?</title>", re.IGNORECASE | re.DOTALL)
DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "references" / "deck.html"

DEFAULT_PORT = 7317
PORT_TRIES = 21  # the default port plus the next 20
MAX_BODY = 1024 * 1024

SAMPLE_RATE = 16000
BYTES_PER_SECOND = SAMPLE_RATE * 2
MAX_UTTERANCE_BYTES = 120 * BYTES_PER_SECOND
PARTIAL_INTERVAL_S = 0.6
PARTIAL_MIN_NEW_BYTES = int(0.4 * BYTES_PER_SECOND)
SILENCE_RMS = 0.003  # below this whisper invents text such as "Thank you."

MLX_MODEL = "mlx-community/whisper-large-v3-turbo"
MLX_ENGINE_NAME = "mlx-whisper large-v3-turbo"

OPENROUTER_API = "https://openrouter.ai/api/v1"
OPENROUTER_PROMPT = "Transcribe this audio verbatim. Output only the transcript."
OPENROUTER_MAX_TRIES = 3


# ---------------------------------------------------------------- shared


def log(message: str) -> None:
    print(f"decision-gui: {message}", file=sys.stderr, flush=True)


def fail(message: str) -> NoReturn:
    sys.exit(f"decision-gui: {message}")


def load_deck(path: Path) -> dict[str, Any]:
    try:
        deck = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"deck not found: {path}")
    except json.JSONDecodeError as e:
        fail(f"deck is not valid JSON: {path}: {e}")
    if not isinstance(deck, dict):
        fail(f"deck must be a JSON object: {path}")
    return deck


def read_template(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"template not found: {path}")


def deck_stem(deck_path: Path) -> str:
    """The deck path minus `.deck.json` (or `.json`): the default output prefix."""
    name = str(deck_path)
    for suffix in (".deck.json", ".json"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def deck_json_for_script(deck: dict[str, Any], mode: str) -> str:
    text = json.dumps({**deck, "mode": mode}, ensure_ascii=False)
    # "</script>" inside a string would close the element early; U+2028/9 break old JS parsers.
    return text.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


LOCAL_SKELETON = (
    '<!doctype html><html><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    "<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}"
    "body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style></head><body>"
)


def render_page(template: str, deck: dict[str, Any], mode: str, template_path: Path) -> str:
    before, found_placeholder, after = template.partition(PLACEHOLDER)
    if not found_placeholder:
        fail(f"template has no {PLACEHOLDER} placeholder: {template_path}")
    title = f"<title>{html.escape(str(deck.get('title', '')))}</title>"
    head, found_title = TITLE_RE.subn(lambda _: title, before[:TITLE_SCAN_CHARS], count=1)
    if not found_title:
        log(f"no <title> in the first 8 KB of {template_path}; title left as is")
    page = head + before[TITLE_SCAN_CHARS:] + deck_json_for_script(deck, mode) + after
    # The Artifact tool wraps a published page in this skeleton; serve the same one locally.
    return LOCAL_SKELETON + page + "</body></html>" if mode == "local" else page


def write_atomic(path: Path, text: str) -> None:
    """Write via a 0600 temp file in the same folder, then rename over the target."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        raise


def template_path_from(arg: str | None) -> Path:
    return Path(arg).expanduser() if arg else DEFAULT_TEMPLATE


# ---------------------------------------------------------------- build


def cmd_build(args: argparse.Namespace) -> None:
    deck_path = Path(args.deck).expanduser()
    deck = load_deck(deck_path)
    template_path = template_path_from(args.template)
    page = render_page(read_template(template_path), deck, "artifact", template_path)
    out = Path(args.out).expanduser() if args.out else Path(deck_stem(deck_path) + ".html")
    out.write_text(page, encoding="utf-8")
    print(out)


# ---------------------------------------------------------------- serve: state


@dataclass
class Server:
    page: str
    out: Path
    executor: ThreadPoolExecutor  # one worker: mlx is not thread-safe, so every decode runs here
    ready: asyncio.Event  # set once the speech engine is chosen (or none is)
    origins: set[str] = field(default_factory=set)
    engine: str | None = None
    kind: str | None = None  # "mlx", "openrouter" or None
    or_key: str = field(default="", repr=False)
    or_models: list[str] = field(default_factory=list)
    http: aiohttp.ClientSession | None = None

    @property
    def streaming(self) -> bool:
        return self.kind == "mlx"


@dataclass
class Utterance:
    pcm: bytearray = field(default_factory=bytearray)
    active: bool = True
    last_partial_at: float = 0.0
    decoded_len: int = 0
    last_text: str = ""
    partial_task: asyncio.Task[None] | None = None


class SttError(Exception):
    """A failure whose message is safe to show on the page."""


def import_server_deps() -> None:
    """Bind aiohttp and numpy late so `build` runs on the standard library alone."""
    global web, np
    try:
        import numpy as np
        from aiohttp import web
    except ImportError as e:
        fail(f"serve needs aiohttp and numpy ({e}). Run: uv run --script {Path(__file__).name} serve ...")


def answer_paths(out: Path) -> tuple[Path, Path]:
    return Path(f"{out}.answers.txt"), Path(f"{out}.answers.json")


def origin_ok(srv: Server, request: web.Request) -> bool:
    return request.headers.get("Origin") in srv.origins


def forbidden() -> web.Response:
    return web.json_response({"ok": False, "error": "origin not allowed"}, status=403)


# ---------------------------------------------------------------- serve: HTTP


async def handle_page(srv: Server, request: web.Request) -> web.Response:
    return web.Response(text=srv.page, content_type="text/html", headers={"Cache-Control": "no-store"})


async def handle_health(srv: Server, request: web.Request) -> web.Response:
    return web.json_response({"ok": True, "engine": srv.engine, "streaming": srv.streaming})


async def handle_save_answers(srv: Server, request: web.Request) -> web.Response:
    if not origin_ok(srv, request):
        return forbidden()
    try:
        body = await request.json()
    except ValueError:
        return web.json_response({"ok": False, "error": "body is not JSON"}, status=400)
    if not (isinstance(body, dict) and isinstance(body.get("text"), str) and isinstance(body.get("state"), dict)):
        return web.json_response({"ok": False, "error": 'body must be {"text": string, "state": object}'}, status=400)
    txt_path, json_path = answer_paths(srv.out)
    saved = {"text": body["text"], "state": body["state"]}
    write_atomic(json_path, json.dumps(saved, ensure_ascii=False, indent=2) + "\n")
    write_atomic(txt_path, body["text"])
    print(f"ANSWERS_SAVED {txt_path}", flush=True)
    return web.json_response({"ok": True, "path": str(txt_path)})


async def handle_load_answers(srv: Server, request: web.Request) -> web.Response:
    _, json_path = answer_paths(srv.out)
    try:
        return web.json_response(json.loads(json_path.read_text(encoding="utf-8")))
    except FileNotFoundError:
        return web.json_response({"ok": False, "error": "no answers saved yet"}, status=404)


# ---------------------------------------------------------------- serve: /stt


async def send(ws: web.WebSocketResponse, message: dict[str, Any]) -> None:
    if ws.closed:
        return
    with contextlib.suppress(ConnectionError, RuntimeError):
        await ws.send_json(message)


async def handle_stt(srv: Server, request: web.Request) -> web.StreamResponse:
    if not origin_ok(srv, request):
        return forbidden()
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    await srv.ready.wait()  # a socket opened during warm-up hears "ready" when warm-up ends
    await send(ws, {"type": "ready", "engine": srv.engine, "streaming": srv.streaming})
    utt: Utterance | None = None
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.BINARY and utt and utt.active:
                add_audio(srv, ws, utt, msg.data)
            elif msg.type == web.WSMsgType.TEXT:
                utt = await handle_command(srv, ws, utt, msg.data)
    finally:
        if utt:
            utt.active = False
    return ws


async def handle_command(srv: Server, ws: web.WebSocketResponse, utt: Utterance | None, raw: str) -> Utterance | None:
    try:
        command = json.loads(raw)
        kind = command.get("type")
    except (ValueError, AttributeError):
        await send(ws, {"type": "error", "message": "The server could not read a message."})
        return utt
    if kind == "start":
        if utt:
            utt.active = False
        if srv.kind is None:
            await send(ws, {"type": "error", "message": "Voice is not available."})
            return None
        rate = command.get("sampleRate", SAMPLE_RATE)
        if rate != SAMPLE_RATE:
            await send(ws, {"type": "error", "message": f"Send 16 kHz audio, not {rate} Hz."})
            return None
        return Utterance()
    if kind == "stop":
        if utt and utt.active:
            utt.active = False
            await finish_utterance(srv, ws, utt)
        return None
    return utt


def add_audio(srv: Server, ws: web.WebSocketResponse, utt: Utterance, data: bytes) -> None:
    room = MAX_UTTERANCE_BYTES - len(utt.pcm)
    if room > 0:
        utt.pcm += data[:room]
    if srv.streaming:
        maybe_start_partial(srv, ws, utt)


def maybe_start_partial(srv: Server, ws: web.WebSocketResponse, utt: Utterance) -> None:
    if utt.partial_task and not utt.partial_task.done():
        return
    now = time.monotonic()
    if now - utt.last_partial_at < PARTIAL_INTERVAL_S:
        return
    if len(utt.pcm) - utt.decoded_len < PARTIAL_MIN_NEW_BYTES:
        return
    utt.last_partial_at, utt.decoded_len = now, len(utt.pcm)
    utt.partial_task = asyncio.create_task(send_partial(srv, ws, utt, bytes(utt.pcm)))


async def send_partial(srv: Server, ws: web.WebSocketResponse, utt: Utterance, pcm: bytes) -> None:
    try:
        text = await run_stt(srv, transcribe_pcm, pcm)
    except Exception as e:
        log(f"partial decode failed: {type(e).__name__}: {e}")
        return
    if utt.active and text and text != utt.last_text:
        utt.last_text = text
        await send(ws, {"type": "partial", "text": text})


async def finish_utterance(srv: Server, ws: web.WebSocketResponse, utt: Utterance) -> None:
    if utt.partial_task:
        # Let an in-flight partial land first so no partial follows the final.
        await asyncio.gather(utt.partial_task, return_exceptions=True)
    pcm = bytes(utt.pcm)
    try:
        if srv.kind == "mlx":
            text = await run_stt(srv, transcribe_pcm, pcm)
        elif is_silent(pcm_to_float(pcm)):
            text = ""
        else:
            text = await transcribe_openrouter(srv, ws, pcm)
    except SttError as e:
        await send(ws, {"type": "error", "message": str(e)})
        return
    except Exception as e:
        log(f"final decode failed: {type(e).__name__}: {e}")
        await send(ws, {"type": "error", "message": "Transcription failed."})
        return
    await send(ws, {"type": "final", "text": text})


async def run_stt(srv: Server, fn: Callable[..., Any], *args: Any) -> Any:
    return await asyncio.get_running_loop().run_in_executor(srv.executor, fn, *args)


# ---------------------------------------------------------------- engines: local whisper


def pcm_to_float(pcm: bytes) -> np.ndarray:
    whole = pcm[: len(pcm) // 2 * 2]
    return np.frombuffer(whole, dtype="<i2").astype(np.float32) / 32768.0


def is_silent(audio: np.ndarray) -> bool:
    return audio.size == 0 or float(np.sqrt(np.mean(np.square(audio)))) < SILENCE_RMS


def run_whisper(audio: np.ndarray) -> str:
    import mlx_whisper

    result = mlx_whisper.transcribe(
        audio,
        path_or_hf_repo=MLX_MODEL,
        language="en",
        temperature=0.0,
        condition_on_previous_text=False,
    )
    return str(result.get("text", "")).strip()


def transcribe_pcm(pcm: bytes) -> str:
    audio = pcm_to_float(pcm)
    return "" if is_silent(audio) else run_whisper(audio)


def warm_mlx() -> None:
    """Load the cached model and decode one second of silence, on the STT thread."""
    run_whisper(np.zeros(SAMPLE_RATE, dtype=np.float32))


# ---------------------------------------------------------------- engines: OpenRouter


def openrouter_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    ref = os.environ.get("DECISION_GUI_OPENROUTER_OP_REF", "").strip()
    if key or not ref:
        return key
    try:
        done = subprocess.run(["op", "read", ref], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        log(f"op read failed: {type(e).__name__}")
        return ""
    if done.returncode != 0:
        log(f"op read failed (exit {done.returncode})")
        return ""
    return done.stdout.strip()


def as_price(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def is_input_price(key: str) -> bool:
    """`prompt` plus audio-input fields; `audio_output` and `input_audio_cache` do not apply to one-shot input."""
    return key == "prompt" or ("audio" in key and "output" not in key and "cache" not in key)


def rank_audio_models(models: list[dict[str, Any]]) -> list[tuple[str, float]]:
    """Audio-input models as (id, price), cheapest first. Zero-priced ones go last: free tiers often train on data."""
    ranked = []
    for model in models:
        modalities = (model.get("architecture") or {}).get("input_modalities") or []
        if "audio" not in modalities or model["id"].endswith((":free", ":batch")):
            continue  # free tiers may train on data; batch variants do not stream
        pricing = model.get("pricing") or {}
        parts = [as_price(v) for k, v in pricing.items() if is_input_price(k)]
        if any(p < 0 for p in parts):
            continue  # -1 marks variable-priced routers such as openrouter/auto
        ranked.append((model["id"], sum(parts)))
    return sorted(ranked, key=lambda r: (r[1] == 0, r[1], r[0]))


async def fetch_audio_models(session: aiohttp.ClientSession) -> list[tuple[str, float]]:
    async with session.get(f"{OPENROUTER_API}/models") as resp:
        resp.raise_for_status()
        payload = await resp.json()
    return rank_audio_models(payload.get("data") or [])


async def setup_openrouter(srv: Server) -> None:
    import aiohttp

    key = await asyncio.to_thread(openrouter_key)
    if not key:
        log("no OpenRouter key (set OPENROUTER_API_KEY or DECISION_GUI_OPENROUTER_OP_REF)")
        return
    srv.http = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120))
    ranked = await fetch_audio_models(srv.http)
    if not ranked:
        log("OpenRouter lists no audio-input models")
        return
    srv.or_key, srv.or_models = key, [model_id for model_id, _ in ranked]
    srv.kind, srv.engine = "openrouter", f"openrouter {srv.or_models[0]}"


def pcm_to_wav(pcm: bytes) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm[: len(pcm) // 2 * 2])
    return buf.getvalue()


async def transcribe_openrouter(srv: Server, ws: web.WebSocketResponse, pcm: bytes) -> str:
    audio_b64 = base64.b64encode(pcm_to_wav(pcm)).decode("ascii")
    for model in srv.or_models[:OPENROUTER_MAX_TRIES]:
        text = await stream_openrouter(srv, ws, model, audio_b64)
        if text is not None:
            return text
    raise SttError("No OpenRouter audio model could transcribe this. See the server log.")


async def stream_openrouter(srv: Server, ws: web.WebSocketResponse, model: str, audio_b64: str) -> str | None:
    """Stream one model's transcript to the page as deltas. None means no endpoint meets the provider rules."""
    assert srv.http is not None
    body = {
        "model": model,
        "stream": True,
        "provider": {"data_collection": "deny", "zdr": True},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": OPENROUTER_PROMPT},
                    {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}},
                ],
            }
        ],
    }
    headers = {"Authorization": f"Bearer {srv.or_key}"}
    async with srv.http.post(f"{OPENROUTER_API}/chat/completions", json=body, headers=headers) as resp:
        if resp.status != 200:
            reason = "no endpoint meets the privacy rules" if "no endpoints" in (await resp.text()).lower() else f"HTTP {resp.status}"
            log(f"OpenRouter {model}: {reason}")
            return None
        parts: list[str] = []
        async for raw in resp.content:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue  # blank separators and ": OPENROUTER PROCESSING" keep-alives
            data = line[len("data:") :].strip()
            if data == "[DONE]":
                break
            event = json.loads(data)
            if "error" in event:
                raise SttError(f"OpenRouter stopped mid-stream for {model}.")
            for choice in event.get("choices") or []:
                piece = (choice.get("delta") or {}).get("content")
                if piece:
                    parts.append(piece)
                    await send(ws, {"type": "delta", "text": piece})
        return "".join(parts).strip()


# ---------------------------------------------------------------- serve: startup


async def init_engine(srv: Server, engine: str) -> None:
    """Pick the speech engine in protocol order, then release sockets waiting for `ready`."""
    try:
        if engine == "auto":
            try:
                await run_stt(srv, warm_mlx)
                srv.kind, srv.engine = "mlx", MLX_ENGINE_NAME
                return
            except Exception as e:
                log(f"local whisper unavailable ({type(e).__name__}: {e}); trying OpenRouter")
        await setup_openrouter(srv)
    except Exception as e:
        log(f"OpenRouter unavailable ({type(e).__name__})")
    finally:
        log(f"speech engine: {srv.engine or 'none, voice is off'}")
        srv.ready.set()


async def bind(runner: web.AppRunner, first_port: int) -> int:
    for port in range(first_port, first_port + PORT_TRIES):
        site = web.TCPSite(runner, "127.0.0.1", port)
        try:
            await site.start()
            return port
        except OSError:
            await site.stop()
    fail(f"ports {first_port}-{first_port + PORT_TRIES - 1} are all taken")


def build_app(srv: Server) -> web.Application:
    app = web.Application(client_max_size=MAX_BODY + 1)  # aiohttp rejects bodies >= the limit
    app.router.add_get("/", functools.partial(handle_page, srv))
    app.router.add_get("/api/health", functools.partial(handle_health, srv))
    app.router.add_post("/api/answers", functools.partial(handle_save_answers, srv))
    app.router.add_get("/api/answers", functools.partial(handle_load_answers, srv))
    app.router.add_get("/stt", functools.partial(handle_stt, srv))
    return app


async def run_server(page: str, out: Path, first_port: int, engine: str) -> None:
    srv = Server(page=page, out=out, executor=ThreadPoolExecutor(1, thread_name_prefix="stt"), ready=asyncio.Event())
    runner = web.AppRunner(build_app(srv), access_log=None)
    await runner.setup()
    init: asyncio.Task[None] | None = None
    try:
        port = await bind(runner, first_port)
        srv.origins = {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}
        print(f"DECISION_GUI_URL http://127.0.0.1:{port}/", flush=True)
        if engine == "none":
            srv.ready.set()
        else:
            init = asyncio.create_task(init_engine(srv, engine))
        await asyncio.Event().wait()
    finally:
        if init:
            init.cancel()
        await runner.cleanup()
        if srv.http:
            await srv.http.close()
        srv.executor.shutdown(wait=False, cancel_futures=True)


def cmd_serve(args: argparse.Namespace) -> None:
    import_server_deps()
    deck_path = Path(args.deck).expanduser()
    deck = load_deck(deck_path)
    template_path = template_path_from(args.template)
    page = render_page(read_template(template_path), deck, "local", template_path)
    out = Path(os.path.abspath(Path(args.out).expanduser() if args.out else deck_stem(deck_path)))
    engine = "none" if args.no_voice else args.engine
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(run_server(page, out, args.port, engine))


# ---------------------------------------------------------------- CLI


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="decision_gui.py", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    build = sub.add_parser("build", help="write a static page (mode artifact)")
    build.add_argument("deck", help="path to DECK.json")
    build.add_argument("--out", help="output HTML (default: deck path with .deck.json -> .html)")
    build.add_argument("--template", help=f"page template (default: {DEFAULT_TEMPLATE})")

    serve = sub.add_parser("serve", help="run the local page server with voice (mode local)")
    serve.add_argument("deck", help="path to DECK.json")
    serve.add_argument("--port", type=int, default=DEFAULT_PORT, help="first port to try (default: %(default)s)")
    serve.add_argument("--out", help="answers prefix (default: deck path minus .deck.json)")
    serve.add_argument("--no-voice", action="store_true", help="turn speech to text off")
    serve.add_argument("--template", help=f"page template (default: {DEFAULT_TEMPLATE})")
    serve.add_argument(
        "--engine", choices=["auto", "openrouter"], default="auto", help="openrouter skips local whisper (testing)"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.cmd == "build":
        cmd_build(args)
    else:
        cmd_serve(args)


if __name__ == "__main__":
    main()
