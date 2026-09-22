import argparse
import html as html_lib
import json
import os
import re
import sqlite3
import sys

EXCERPT_CHARS = 900


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def parse_duration(text):
    m = re.fullmatch(r"(\d+)(s|m|h)", text.strip())
    if not m:
        die(f"unknown duration: {text}")
    n = int(m.group(1))
    unit = m.group(2)
    if unit == "s":
        return n
    if unit == "m":
        return n * 60
    return n * 3600


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        die(f"missing file: {path}")
    except json.JSONDecodeError:
        die(f"invalid json: {path}")


def load_chunks(path):
    chunks = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                row = json.loads(line)
                chunks[row["id"]] = row
    return chunks


def load_scores(paths):
    scores = {}
    for path in paths or []:
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        row = json.loads(line)
                        scores[row["id"]] = row
        except OSError:
            die(f"missing file: {path}")
    return scores


def rubric_categories(rubric):
    raw = rubric.get("categories") or {}
    if isinstance(raw, dict):
        return [{"key": k, "label": (v.get("label") if isinstance(v, dict) else k) or k} for k, v in raw.items()]
    if isinstance(raw, list):
        out = []
        for item in raw:
            if isinstance(item, str):
                out.append({"key": item, "label": item})
            elif isinstance(item, dict) and "key" in item:
                out.append({"key": item["key"], "label": item.get("label", item["key"])})
        return out
    return []


def build_payload(chunks, scores, rubric, chunk_seconds, bar_seconds, title, subtitle):
    tiers = rubric.get("tiers")
    if not tiers:
        die("rubric missing tiers")
    cat_defs = rubric_categories(rubric)
    cat_keys = [c["key"] for c in cat_defs]

    notes = []
    part_stats = {}

    for cid in sorted(chunks.keys(), key=lambda x: (chunks[x]["part"], chunks[x]["chunk_index"])):
        chunk = chunks[cid]
        score = scores.get(cid)
        part = chunk["part"]
        ps = part_stats.setdefault(
            part,
            {
                "part": part,
                "label": chunk.get("part_label") or f"Part {part}",
                "chunk_count": 0,
                "scored_count": 0,
                "first_start_s": chunk["start_s"],
                "last_end_s": chunk["end_s"],
            },
        )
        ps["chunk_count"] += 1
        ps["first_start_s"] = min(ps["first_start_s"], chunk["start_s"])
        ps["last_end_s"] = max(ps["last_end_s"], chunk["end_s"])
        if score is not None:
            ps["scored_count"] += 1

        cats = {}
        for key in cat_keys:
            entry = (score or {}).get("categories", {}).get(key) if score else None
            cats[key] = {
                "tier": entry["tier"] if entry else None,
                "tier_index": entry["tier_index"] if entry else None,
                "expected": entry["expected"] if entry else None,
                "confidence": entry["confidence"] if entry else None,
            }

        notes.append(
            {
                "id": cid,
                "part": part,
                "chunk_index": chunk["chunk_index"],
                "start_s": chunk["start_s"],
                "end_s": chunk["end_s"],
                "words": chunk["words"],
                "excerpt": chunk["text"][:EXCERPT_CHARS],
                "text": chunk["text"],
                "scored": score is not None,
                "categories": cats,
            }
        )

    parts = [part_stats[k] for k in sorted(part_stats.keys())]
    scored_count = sum(1 for n in notes if n["scored"])

    return {
        "title": title or rubric.get("title") or "Transcript heatmap",
        "subtitle": subtitle if subtitle is not None else rubric.get("subtitle") or "",
        "tiers": tiers,
        "categories": cat_defs,
        "chunk_seconds": chunk_seconds,
        "bar_seconds": bar_seconds,
        "parts": parts,
        "scored_count": scored_count,
        "total_count": len(notes),
        "notes": notes,
    }


def write_sqlite(path, chunks, notes):
    if os.path.exists(path):
        os.remove(path)
    db = sqlite3.connect(path)
    db.execute(
        """CREATE TABLE chunk (
        id TEXT PRIMARY KEY, part INTEGER, part_label TEXT, chunk_index INTEGER,
        start_s INTEGER, end_s INTEGER, words INTEGER, scored INTEGER, text TEXT)"""
    )
    db.execute(
        """CREATE TABLE score (
        id TEXT, category TEXT, tier TEXT, tier_index INTEGER, expected REAL, confidence REAL,
        PRIMARY KEY (id, category))"""
    )
    for note in notes:
        chunk = chunks[note["id"]]
        db.execute(
            "INSERT INTO chunk VALUES (?,?,?,?,?,?,?,?,?)",
            (
                note["id"],
                note["part"],
                chunk.get("part_label") or f"Part {note['part']}",
                note["chunk_index"],
                note["start_s"],
                note["end_s"],
                note["words"],
                int(note["scored"]),
                note["text"],
            ),
        )
        for category, entry in note["categories"].items():
            if entry.get("tier") is None:
                continue
            db.execute(
                "INSERT INTO score VALUES (?,?,?,?,?,?)",
                (
                    note["id"],
                    category,
                    entry["tier"],
                    entry["tier_index"],
                    entry["expected"],
                    entry["confidence"],
                ),
            )
    db.commit()
    db.close()


def inline_page(shell_path, shell_text, data):
    shell_dir = os.path.dirname(os.path.abspath(shell_path))
    css_path = os.path.join(shell_dir, "app.css")
    js_path = os.path.join(shell_dir, "app.js")
    try:
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        with open(js_path, encoding="utf-8") as f:
            js = f.read()
    except OSError as e:
        die(f"missing asset next to shell: {e}")

    payload = json.dumps(data, ensure_ascii=False)
    html = shell_text
    html = re.sub(
        r'<link\s+rel="stylesheet"\s+href="app\.css"\s*/?>',
        f"<style>\n{css}\n</style>",
        html,
        count=1,
    )
    def inject_js(_match):
        return (
            f"<script>window.HEATMAP_DATA = {payload};</script>\n"
            f"<script>\n{js}\n</script>"
        )

    html = re.sub(
        r'<script\s+src="app\.js"\s*></script>',
        inject_js,
        html,
        count=1,
    )
    html = re.sub(r'<script\s+src="data\.js"\s*></script>\s*', "", html)
    title = html_lib.escape(data["title"])
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.S)
    return html


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks", required=True)
    parser.add_argument("--rubric", required=True)
    parser.add_argument("--shell", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--scores", action="append", default=[])
    parser.add_argument("--title", default=None)
    parser.add_argument("--subtitle", default=None)
    parser.add_argument("--bar", default="4h")
    parser.add_argument("--sqlite", default=None)
    parser.add_argument("--data-out", default=None)
    parser.add_argument("--standalone", action="store_true")
    args = parser.parse_args()

    try:
        with open(args.shell, encoding="utf-8") as f:
            shell_text = f.read()
    except OSError:
        die(f"missing file: {args.shell}")

    rubric = load_json(args.rubric)
    chunks = load_chunks(args.chunks)
    scores = load_scores(args.scores)

    chunk_seconds = 300
    if chunks:
        deltas = [c["end_s"] - c["start_s"] for c in chunks.values()]
        chunk_seconds = max(set(deltas), key=deltas.count)

    bar_seconds = parse_duration(args.bar)
    data = build_payload(
        chunks,
        scores,
        rubric,
        chunk_seconds,
        bar_seconds,
        args.title,
        args.subtitle,
    )

    html = inline_page(args.shell, shell_text, data)
    if args.standalone:
        title_match = re.search(r"<title>.*?</title>", html, flags=re.S)
        title_tag = title_match.group(0) if title_match else "<title>Transcript heatmap</title>"
        body = html.replace(title_tag, "", 1).lstrip("\n")
        html = (
            "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"{title_tag}\n</head>\n<body>\n{body}\n</body>\n</html>"
        )

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)

    if args.data_out:
        with open(args.data_out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    if args.sqlite:
        write_sqlite(args.sqlite, chunks, data["notes"])

    nbytes = os.path.getsize(args.out)
    print(
        f"parts {len(data['parts'])}, chunks {data['total_count']}, "
        f"scored {data['scored_count']}/{data['total_count']}, "
        f"categories {len(data['categories'])}, tiers {len(data['tiers'])}, "
        f"bytes {nbytes} -> {args.out}"
    )


if __name__ == "__main__":
    main()
