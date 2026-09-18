import argparse
import concurrent.futures as cf
import json
import subprocess
import sys
import threading
import time

ledger_lock = threading.Lock()
done_count = 0
fail_count = 0
start_time = time.time()


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        die(f"missing file: {path}")
    except json.JSONDecodeError:
        die(f"invalid json: {path}")


def load_chunks(path, parts_filter):
    chunks = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    chunks.append(json.loads(line))
    except OSError:
        die(f"missing file: {path}")
    if parts_filter:
        chunks = [c for c in chunks if c.get("part") in parts_filter]
    return chunks


def load_done(path):
    ids = set()
    if not path:
        return ids
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    ids.add(json.loads(line)["id"])
    except OSError:
        pass
    return ids


def call_scorer(cmd, chunk, rubric, retries):
    payload = json.dumps({"chunk": chunk, "rubric": rubric})
    for attempt in range(retries + 1):
        proc = subprocess.run(
            cmd,
            input=payload,
            capture_output=True,
            text=True,
            shell=True,
        )
        if proc.returncode != 0:
            reason = (proc.stderr or proc.stdout or "non-zero exit").strip()[:160]
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
                continue
            return None, reason
        try:
            result = json.loads(proc.stdout)
        except json.JSONDecodeError:
            reason = "unparseable stdout"
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
                continue
            return None, reason
        return result, None
    return None, "failed"


def row_for(chunk, result, tiers, rubric_cats):
    row = {
        "id": chunk["id"],
        "part": chunk["part"],
        "chunk_index": chunk["chunk_index"],
        "start_s": chunk["start_s"],
        "words": chunk["words"],
        "categories": {},
    }
    categories = (result or {}).get("categories") or {}
    for key in rubric_cats:
        if key not in categories:
            continue
        answer = categories[key] or {}
        tier = answer.get("tier")
        tier_index = tiers.index(tier) if tier in tiers else None
        probs = answer.get("probabilities") or {}
        if probs:
            expected = round(sum(tiers.index(t) * p for t, p in probs.items() if t in tiers), 3)
            confidence = round(max(probs.values()), 3) if probs else None
        else:
            expected = tier_index
            confidence = None
        row["categories"][key] = {
            "tier": tier,
            "tier_index": tier_index,
            "expected": expected,
            "confidence": confidence,
        }
    return row


def work(chunk, total, cmd, rubric, tiers, rubric_cats, out_path, retries):
    global done_count, fail_count
    result, reason = call_scorer(cmd, chunk, rubric, retries)
    if result is None:
        print(f"  {chunk['id']} FAILED {reason}", flush=True)
        with ledger_lock:
            fail_count += 1
        return False
    row = row_for(chunk, result, tiers, rubric_cats)
    with ledger_lock:
        with open(out_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        done_count += 1
        n = done_count
        rate = n / max(time.time() - start_time, 1) * 60
        parts = []
        for k, v in row["categories"].items():
            tier = v.get("tier") or "?"
            exp = v.get("expected")
            exp_s = f"{exp:.2f}" if isinstance(exp, (int, float)) else "?"
            parts.append(f"{k[:4]}={tier[:4]}/{exp_s}")
        summary = " ".join(parts)
        print(f"  [{n}/{total}] {chunk['id']} {summary} ({rate:.1f}/min)", flush=True)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks", required=True)
    parser.add_argument("--rubric", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--cmd", required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--part", type=int, action="append", default=[])
    args = parser.parse_args()

    rubric = load_json(args.rubric)
    tiers = rubric.get("tiers")
    if not tiers:
        die("rubric missing tiers")
    rubric_cats = list((rubric.get("categories") or {}).keys())

    parts_filter = set(args.part) if args.part else None
    chunks = load_chunks(args.chunks, parts_filter)
    done = load_done(args.out)
    todo = [c for c in chunks if c["id"] not in done]
    if args.limit is not None:
        todo = todo[: args.limit]

    print(
        f"{len(done)} scored, {len(todo)} to go, {args.workers} workers",
        flush=True,
    )
    if not todo:
        return

    successes = 0
    with cf.ThreadPoolExecutor(args.workers) as ex:
        futures = [
            ex.submit(
                work,
                c,
                len(todo),
                args.cmd,
                rubric,
                tiers,
                rubric_cats,
                args.out,
                args.retries,
            )
            for c in todo
        ]
        for fut in futures:
            if fut.result():
                successes += 1

    if successes == 0 and len(todo) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
