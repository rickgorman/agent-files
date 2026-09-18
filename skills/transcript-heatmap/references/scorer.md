# External scorer contract

The default scoring lane is subagents: they read the rubric and a batch of chunks and write
ledger rows. `scripts/score.py --cmd "<command>"` is the other lane — any classifier you can
run from a shell, one process per chunk, with concurrency, retries, and resume handled for
you. Use it when you have a cheap tiered classifier and thousands of chunks.

## The command

`score.py` runs `<command>` through the shell once per unscored chunk.

**stdin** — one JSON object:

```json
{
  "chunk": {"id": "p1-030", "part": 1, "part_label": "Day 1", "chunk_index": 30,
            "start_s": 9000, "end_s": 9300, "words": 857, "text": "..."},
  "rubric": {"tiers": ["noise", "..."], "context": "...", "categories": {"...": {}}}
}
```

**stdout** — one JSON object, nothing else:

```json
{
  "categories": {
    "agentic_engineering": {
      "tier": "explained",
      "probabilities": {"noise": 0.01, "mention": 0.10, "demo": 0.08,
                        "explained": 0.77, "masterclass": 0.04}
    }
  }
}
```

`probabilities` is optional. When it is there, the ledger's `expected` is the
probability-weighted tier index — a fractional tier, which is what makes neighbouring notes
comparable instead of both reading "demo". When it is absent, `expected` is the tier index
and `confidence` is null.

A category you omit is unscored for that chunk. A category name that is not in the rubric is
ignored. Exit non-zero, or print anything that is not JSON, and `score.py` retries with
backoff, then records the chunk as failed and moves on.

## Smallest working example

```python
#!/usr/bin/env python3
import json, sys

payload = json.load(sys.stdin)
chunk, rubric = payload["chunk"], payload["rubric"]
# call your model here with rubric["context"], the category instructions, and chunk["text"]
print(json.dumps({"categories": {key: {"tier": "noise"} for key in rubric["categories"]}}))
```

```bash
python3 scripts/score.py --chunks chunks.jsonl --rubric rubric.json \
  --out scores.jsonl --cmd "python3 my_scorer.py" --workers 8
```

## Notes

- Rate limits are the usual reason a run stalls. Lower `--workers` before raising `--retries`.
- `--limit N` scores N chunks and stops — the cheap way to calibrate a rubric.
- The ledger is append-only. Deleting it re-scores everything; deleting nothing re-scores
  only what is missing.
