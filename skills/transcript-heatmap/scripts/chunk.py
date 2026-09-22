import argparse
import glob
import json
import os
import re
import sys

SRT_ARROW = re.compile(
    r"^\s*(\d{1,2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[.,]\d{3})\s*$"
)
WHISPER_ARROW = re.compile(
    r"^\[(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)\s*-->\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)\]\s*(.*)$"
)
BRACKET_MARKER = re.compile(r"^\[(\d{1,2}:\d{2}:\d{2})\]\s*$")
INLINE_TS = re.compile(
    r"^(?:\((\d{1,2}:\d{2}(?::\d{2})?)\)|(\d{1,2}:\d{2}:\d{2}|\d{1,2}:\d{2}))\s+(.*)$"
)


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


def to_seconds(stamp):
    stamp = stamp.strip().replace(",", ".")
    if "." in stamp:
        head, frac = stamp.split(".", 1)
        frac_s = float("0." + frac)
    else:
        head = stamp
        frac_s = 0.0
    parts = head.split(":")
    nums = [float(p) for p in parts]
    if len(nums) == 1:
        base = nums[0]
    elif len(nums) == 2:
        base = nums[0] * 60 + nums[1]
    else:
        base = nums[0] * 3600 + nums[1] * 60 + nums[2]
    return base + frac_s


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def segments_srt_vtt(text):
    blocks = re.split(r"\n\s*\n", text.strip())
    segments = []
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        if lines[0].upper() == "WEBVTT" or lines[0].startswith("NOTE"):
            continue
        idx = 0
        if re.fullmatch(r"\d+", lines[0]):
            idx = 1
        if idx >= len(lines):
            continue
        m = SRT_ARROW.match(lines[idx])
        if not m:
            continue
        start = to_seconds(m.group(1))
        end = to_seconds(m.group(2))
        body = " ".join(lines[idx + 1 :]).strip()
        if body:
            segments.append((start, end, body))
    return segments if segments else None


def segments_whisper(text):
    segments = []
    for line in text.splitlines():
        m = WHISPER_ARROW.match(line.strip())
        if m and m.group(3).strip():
            segments.append((to_seconds(m.group(1)), to_seconds(m.group(2)), m.group(3).strip()))
    return segments if segments else None


def _close_marker_segments(raw, wpm):
    segments = []
    for i, (start, body) in enumerate(raw):
        if i + 1 < len(raw):
            end = raw[i + 1][0]
        else:
            end = start + len(body.split()) / wpm * 60
        segments.append((start, end, body))
    return segments


def segments_bracket_markers(text, wpm):
    raw = []
    start = None
    buf = []
    for line in text.splitlines():
        raw_line = line.strip()
        if not raw_line:
            continue
        m = BRACKET_MARKER.match(raw_line)
        if m:
            if start is not None and buf:
                raw.append((start, " ".join(buf)))
            start = to_seconds(m.group(1))
            buf = []
            continue
        if start is not None:
            buf.append(raw_line)
    if start is not None and buf:
        raw.append((start, " ".join(buf)))
    if not raw:
        return None
    return _close_marker_segments(raw, wpm)


def segments_inline(text, wpm):
    raw = []
    for line in text.splitlines():
        raw_line = line.strip()
        if not raw_line:
            continue
        m = INLINE_TS.match(raw_line)
        if m:
            stamp = m.group(1) or m.group(2)
            body = m.group(3).strip()
            if body:
                raw.append((to_seconds(stamp), body))
    if not raw:
        return None
    return _close_marker_segments(raw, wpm)


def segments_wpm(text, wpm):
    words = text.split()
    if not words:
        return None
    segments = []
    sec_per_word = 60.0 / wpm
    pos = 0.0
    chunk_words = []
    for w in words:
        chunk_words.append(w)
        if len(chunk_words) >= 40:
            start = pos
            pos += len(chunk_words) * sec_per_word
            segments.append((start, pos, " ".join(chunk_words)))
            chunk_words = []
    if chunk_words:
        start = pos
        pos += len(chunk_words) * sec_per_word
        segments.append((start, pos, " ".join(chunk_words)))
    return segments


def detect_and_parse(text, wpm):
    for name, fn in (
        ("srt_vtt", lambda: segments_srt_vtt(text)),
        ("whisper_arrow", lambda: segments_whisper(text)),
        ("bracket_markers", lambda: segments_bracket_markers(text, wpm)),
        ("inline_timestamps", lambda: segments_inline(text, wpm)),
    ):
        segs = fn()
        if segs:
            return name, segs
    segs = segments_wpm(text, wpm)
    if segs:
        return "synthesized_wpm", segs
    return None, None


def collect_files(source):
    if os.path.isfile(source):
        return [source]
    if os.path.isdir(source):
        paths = []
        for ext in ("srt", "vtt", "txt"):
            paths.extend(glob.glob(os.path.join(source, f"*.{ext}")))
        paths = sorted(set(paths))
        if not paths:
            die(f"no transcript files in directory: {source}")
        return paths
    die(f"source not found: {source}")


def parse_source(path, offset, wpm):
    text = read_text(path)
    fmt, segments = detect_and_parse(text, wpm)
    if not segments:
        die(f"could not parse transcript: {path}")
    shifted = []
    file_end = offset
    for start, end, body in segments:
        s = start + offset
        e = end + offset
        if e < s:
            e = s
        shifted.append((s, e, body))
        file_end = max(file_end, e)
    return fmt, shifted, file_end


def _bucket_overlaps(start, end, chunk_seconds):
    overlaps = []
    b = int(start // chunk_seconds)
    while b * chunk_seconds < end:
        b_start = b * chunk_seconds
        b_end = (b + 1) * chunk_seconds
        o_start = max(start, b_start)
        o_end = min(end, b_end)
        if o_end > o_start:
            overlaps.append((b, o_end - o_start))
        b += 1
    return overlaps


def bin_segments(part, part_label, chunk_seconds, segments):
    bins = {}
    for start, end, body in segments:
        words = body.split()
        if not words:
            continue
        duration = end - start
        if duration <= 0:
            idx = int(start // chunk_seconds)
            bins.setdefault(idx, []).append(body)
            continue
        overlaps = _bucket_overlaps(start, end, chunk_seconds)
        if not overlaps:
            idx = int(start // chunk_seconds)
            bins.setdefault(idx, []).append(body)
            continue
        word_idx = 0
        for i, (b_idx, t_in) in enumerate(overlaps):
            if i == len(overlaps) - 1:
                n = len(words) - word_idx
            else:
                n = int(len(words) * t_in / duration)
            if n <= 0:
                continue
            piece = " ".join(words[word_idx : word_idx + n])
            word_idx += n
            bins.setdefault(b_idx, []).append(piece)
    chunks = []
    for idx in sorted(bins):
        text = " ".join(bins[idx]).strip()
        if not text:
            continue
        row = {
            "id": f"p{part}-{idx:03d}",
            "part": part,
            "part_label": part_label,
            "chunk_index": idx,
            "start_s": idx * chunk_seconds,
            "end_s": (idx + 1) * chunk_seconds,
            "words": len(text.split()),
            "text": text,
        }
        chunks.append(row)
    return chunks


def format_span(chunks):
    if not chunks:
        return "0:00 -> 0:00"
    a, b = chunks[0]["start_s"], chunks[-1]["end_s"]
    return f"{a // 3600}:{a % 3600 // 60:02d} -> {b // 3600}:{b % 3600 // 60:02d}"


def median_words(chunks):
    if not chunks:
        return 0
    vals = sorted(c["words"] for c in chunks)
    return vals[len(vals) // 2]


def emit_chunk_line(row):
    ordered = {
        "id": row["id"],
        "part": row["part"],
        "part_label": row["part_label"],
        "chunk_index": row["chunk_index"],
        "start_s": row["start_s"],
        "end_s": row["end_s"],
        "words": row["words"],
        "text": row["text"],
    }
    return json.dumps(ordered, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", nargs="+")
    parser.add_argument("--out", required=True)
    parser.add_argument("--chunk", default="5m")
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--wpm", type=int, default=150)
    args = parser.parse_args()

    chunk_seconds = parse_duration(args.chunk)
    all_chunks = []
    summaries = []

    for i, source in enumerate(args.sources):
        part = i + 1
        if i < len(args.label):
            label = args.label[i]
        else:
            label = f"Part {part}"
        paths = collect_files(source)
        offset = 0.0
        fmt_used = None
        part_segments = []
        for path in paths:
            fmt, segs, file_end = parse_source(path, offset, args.wpm)
            fmt_used = fmt
            part_segments.extend(segs)
            offset = file_end
        part_chunks = bin_segments(part, label, chunk_seconds, part_segments)
        all_chunks.extend(part_chunks)
        summaries.append((part, label, part_chunks, fmt_used))

    with open(args.out, "w", encoding="utf-8") as out:
        for row in all_chunks:
            out.write(emit_chunk_line(row) + "\n")

    total = 0
    for part, label, chunks, fmt in summaries:
        total += len(chunks)
        print(
            f"part {part} ({label}): {len(chunks)} chunks, {format_span(chunks)}, "
            f"median {median_words(chunks)} words, format {fmt}"
        )
    print(f"total {total} chunks -> {args.out}")


if __name__ == "__main__":
    main()
