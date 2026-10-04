#!/usr/bin/env python3
"""Generate text hints for every page of a prepared run.

Runs as part of `editppt prepare`, after page directories exist: each
`pages/page_NNN/` receives canonical `text_hints.json` and `text_hints.png`
files so page workers find their text measurements already in place.

Text hints use the built-in offline detector (`text_hints.py`) per page: it
measures where text sits and how large it is from the page ink, without any
network call.

Hint generation is best-effort: a page that fails is reported and skipped,
and the page worker can regenerate with `editppt page hints <page_dir>`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

from deck_run_state import load_deck, load_jobs, page_dir_for, run_dir_from_target
from text_hints import draw_overlay, page_text_hints

HINTS_JSON = "text_hints.json"
HINTS_PNG = "text_hints.png"
BACKEND = "builtin-ink"


def write_hints(page_dir: Path, hints: dict, overlay: bool) -> None:
    (page_dir / HINTS_JSON).write_text(json.dumps(hints, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if overlay:
        draw_overlay(Image.open(page_dir / "source.png"), hints["lines"], page_dir / HINTS_PNG)


def builtin_page(page_dir: Path) -> dict:
    hints = page_text_hints(page_dir)
    hints["backend"] = BACKEND
    return hints


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate per-page text hints for a prepared run.")
    parser.add_argument("run", help="Run directory or deck_manifest.json path.")
    parser.add_argument("--no-overlay", action="store_true", help="Skip the labeled overlay images.")
    args = parser.parse_args()

    run_dir = run_dir_from_target(args.run)
    deck = load_deck(run_dir)
    jobs = load_jobs(run_dir)
    page_dirs = [page_dir_for(run_dir, page) for page in jobs.get("pages", [])]
    page_dirs = [d for d in page_dirs if (d / "source.png").exists()]
    if not page_dirs:
        print("text-hints: no pages with source.png; skipped", file=sys.stderr)
        return 0

    written = 0
    for page_dir in page_dirs:
        try:
            hints = builtin_page(page_dir)
            write_hints(page_dir, hints, overlay=not args.no_overlay)
            written += 1
        except Exception as exc:
            print(f"text-hints: {page_dir.name} failed ({exc}); worker can run `editppt page hints` itself", file=sys.stderr)
    print(f"text-hints: wrote {written}/{len(page_dirs)} pages (backend={BACKEND})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
