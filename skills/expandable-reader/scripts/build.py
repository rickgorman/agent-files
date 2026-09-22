#!/usr/bin/env python3
"""Inject content.json (plus optional lens files) into shell.html as window.GUIDE.

Usage:
  build.py --shell references/shell.html --content content.json [--lens a.json ...] --out page.html [--standalone]
"""
import argparse
import json
import re
import sys


def count_nodes(nodes):
    return sum(1 + count_nodes(n.get("children", [])) for n in nodes)


def count_spans(obj):
    if isinstance(obj, dict):
        n = 1 if "t" in obj and "zoom" in obj else 0
        return n + sum(count_spans(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_spans(v) for v in obj)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shell", required=True)
    ap.add_argument("--content", required=True)
    ap.add_argument("--lens", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--standalone", action="store_true")
    args = ap.parse_args()

    guide = json.load(open(args.content))
    for path in args.lens:
        guide["sections"] = guide["sections"] + json.load(open(path))["sections"]

    shell = open(args.shell).read()
    m = re.search(r'(<script id="guide-data">)(.*?)(</script>)', shell, re.S)
    if not m:
        sys.exit("guide-data script block not found in shell")
    payload = json.dumps(guide, ensure_ascii=False, indent=1).replace("</", "<\\/")
    page = shell[: m.start(2)] + "\nwindow.GUIDE = " + payload + ";\n" + shell[m.end(2):]
    page = re.sub(r"<title>.*?</title>", "<title>" + guide["title"] + "</title>", page, count=1, flags=re.S)

    if args.standalone:
        page = (
            '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            "<style>[hidden]{display:none!important}body{margin:0}</style>\n</head>\n<body>\n"
            + page
            + "\n</body>\n</html>\n"
        )

    open(args.out, "w").write(page)
    crux_words = sum(
        len((s if isinstance(s, str) else s["t"]).split()) for para in guide["crux"] for s in para
    )
    print(
        f"sections {len(guide['sections'])} nodes {sum(count_nodes(s['nodes']) for s in guide['sections'])} "
        f"spans {count_spans(guide)} crux_words {crux_words} bytes {len(page)} -> {args.out}"
    )


if __name__ == "__main__":
    main()
