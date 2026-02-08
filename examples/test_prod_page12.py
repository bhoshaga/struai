#!/usr/bin/env python3
"""Portable Tier 1 drawings workflow example."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from struai import StruAI


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a drawings-only SDK workflow")
    parser.add_argument(
        "--pdf",
        default=os.environ.get("STRUAI_PDF"),
        help="Path to source PDF (or set STRUAI_PDF)",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=int(os.environ.get("STRUAI_PAGE", "12")),
        help="1-indexed page number",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("STRUAI_API_KEY"),
        help="API key (or set STRUAI_API_KEY)",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("STRUAI_BASE_URL", "https://api.stru.ai"),
        help="Base URL (SDK appends /v1 automatically when needed)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the drawing result at the end",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if not args.api_key:
        print("Missing API key. Pass --api-key or set STRUAI_API_KEY.")
        return 1

    if not args.pdf:
        print("Missing PDF path. Pass --pdf or set STRUAI_PDF.")
        return 1

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return 1

    client = StruAI(api_key=args.api_key, base_url=args.base_url)

    file_hash = client.drawings.compute_file_hash(pdf_path)
    cache = client.drawings.check_cache(file_hash)
    print(f"file_hash={file_hash} cached={cache.cached}")

    if cache.cached:
        result = client.drawings.analyze(page=args.page, file_hash=file_hash)
    else:
        result = client.drawings.analyze(file=str(pdf_path), page=args.page)

    print(f"drawing_id={result.id} page={result.page} processing_ms={result.processing_ms}")
    print(
        "leaders="
        f"{len(result.annotations.leaders)} "
        "section_tags="
        f"{len(result.annotations.section_tags)} "
        "detail_tags="
        f"{len(result.annotations.detail_tags)} "
        "revision_triangles="
        f"{len(result.annotations.revision_triangles)} "
        "revision_clouds="
        f"{len(result.annotations.revision_clouds)}"
    )

    fetched = client.drawings.get(result.id)
    print(f"get_drawing_id={fetched.id} get_page={fetched.page}")

    if args.delete:
        deleted = client.drawings.delete(result.id)
        print(f"deleted={deleted.deleted} drawing_id={deleted.id}")
    else:
        print(f"kept_drawing_id={result.id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
