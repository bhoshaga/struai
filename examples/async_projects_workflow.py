#!/usr/bin/env python3
"""Async SDK workflow example (Tier 1 + Tier 2)."""

from __future__ import annotations

import argparse
import asyncio
import os
import time
from pathlib import Path

from struai import AsyncStruAI


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run async StruAI workflow")
    parser.add_argument("--pdf", default=os.environ.get("STRUAI_PDF"), help="Path to PDF")
    parser.add_argument(
        "--page",
        type=int,
        default=int(os.environ.get("STRUAI_PAGE", "12")),
        help="1-indexed page number",
    )
    parser.add_argument("--api-key", default=os.environ.get("STRUAI_API_KEY"), help="API key")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("STRUAI_BASE_URL", "https://api.stru.ai"),
        help="Base URL",
    )
    parser.add_argument("--cleanup", action="store_true", help="Delete project at end")
    return parser.parse_args()


async def _run(args: argparse.Namespace) -> int:
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

    async with AsyncStruAI(api_key=args.api_key, base_url=args.base_url) as client:
        file_hash = client.drawings.compute_file_hash(pdf_path)
        cache = await client.drawings.check_cache(file_hash)

        if cache.cached:
            drawing = await client.drawings.analyze(page=args.page, file_hash=file_hash)
        else:
            drawing = await client.drawings.analyze(file=str(pdf_path), page=args.page)
        print(f"drawing_id={drawing.id} page={drawing.page}")

        project = await client.projects.create(name=f"Async SDK Workflow {int(time.time())}")
        print(f"project_id={project.id}")

        ingest = await project.sheets.add(page=args.page, file_hash=file_hash)
        if hasattr(ingest, "wait_all"):
            sheet_result = (await ingest.wait_all(timeout_per_job=180, poll_interval=2))[0]
        else:
            sheet_result = await ingest.wait(timeout=180, poll_interval=2)
        print(f"sheet_id={sheet_result.sheet_id}")

        search = await project.search("beam connection", limit=5)
        print(
            f"search entities={len(search.entities)} "
            f"facts={len(search.facts)} communities={len(search.communities)}"
        )

        if args.cleanup:
            deleted = await project.delete()
            print(f"project_deleted={deleted.deleted} id={deleted.id}")
        else:
            print(f"kept_project_id={project.id}")

    return 0


def main() -> int:
    args = _parse_args()
    return asyncio.run(_run(args))


if __name__ == "__main__":
    raise SystemExit(main())
