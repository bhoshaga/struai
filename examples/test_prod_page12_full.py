#!/usr/bin/env python3
"""Portable end-to-end Tier 1 + Tier 2 SDK workflow example."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Any, List

from struai import StruAI


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run full StruAI workflow")
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
        "--query",
        default="beam connection",
        help="Search query to run after ingestion",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=240.0,
        help="Job wait timeout seconds",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Job poll interval seconds",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete created sheet and project at end",
    )
    return parser.parse_args()


def _wait_ingest(result_or_batch: Any, timeout: float, poll_interval: float):
    if hasattr(result_or_batch, "wait_all"):
        statuses = result_or_batch.status_all()
        status_summary = [(s.job_id, s.status) for s in statuses]
        print(f"initial_batch_statuses={status_summary}")

        results = result_or_batch.wait_all(timeout_per_job=timeout, poll_interval=poll_interval)
        for result in results:
            if getattr(result, "sheet_id", None):
                return result
        return results[0]

    status = result_or_batch.status()
    print(f"initial_job_status job_id={status.job_id} status={status.status}")
    return result_or_batch.wait(timeout=timeout, poll_interval=poll_interval)


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

    print("== Tier 1: Drawings ==")
    file_hash = client.drawings.compute_file_hash(pdf_path)
    cache = client.drawings.check_cache(file_hash)
    print(f"file_hash={file_hash} cached={cache.cached}")

    if cache.cached:
        drawing = client.drawings.analyze(page=args.page, file_hash=file_hash)
    else:
        drawing = client.drawings.analyze(file=str(pdf_path), page=args.page)

    print(f"drawing_id={drawing.id} page={drawing.page} processing_ms={drawing.processing_ms}")

    print("\n== Tier 2: Projects ==")
    project_name = f"SDK Workflow {int(time.time())}"
    project = client.projects.create(
        name=project_name,
        description=f"Created from {pdf_path.name} page {args.page}",
    )
    print(f"project_created id={project.id} name={project.name}")

    projects: List[Any] = client.projects.list(limit=5)
    print(f"projects_list_count={len(projects)}")

    fetched_project = client.projects.get(project.id)
    print(f"project_get id={fetched_project.id} description={fetched_project.description}")

    if cache.cached:
        ingest = project.sheets.add(
            page=args.page,
            file_hash=file_hash,
            source_description=f"{pdf_path.name} page {args.page}",
            on_sheet_exists="skip",
            community_update_mode="incremental",
            semantic_index_update_mode="incremental",
        )
    else:
        ingest = project.sheets.add(
            file=str(pdf_path),
            page=args.page,
            source_description=f"{pdf_path.name} page {args.page}",
            on_sheet_exists="skip",
            community_update_mode="incremental",
            semantic_index_update_mode="incremental",
        )

    sheet_result = _wait_ingest(ingest, timeout=args.timeout, poll_interval=args.poll_interval)
    print(
        f"sheet_result sheet_id={sheet_result.sheet_id} "
        f"entities_created={sheet_result.entities_created} "
        f"relationships_created={sheet_result.relationships_created}"
    )

    sheets = project.sheets.list(limit=10)
    print(f"sheets_list_count={len(sheets)}")

    if not sheet_result.sheet_id:
        print("No sheet_id returned from ingest; skipping sheet detail calls.")
        target_sheet_id = None
    else:
        target_sheet_id = sheet_result.sheet_id

    if target_sheet_id:
        sheet = project.sheets.get(target_sheet_id)
        print(f"sheet_get id={sheet.id} page={sheet.page} regions={len(sheet.regions)}")

        annotations = project.sheets.get_annotations(target_sheet_id)
        print(
            "sheet_annotations leaders="
            f"{len(annotations.annotations.get('leaders', []))} "
            "section_tags="
            f"{len(annotations.annotations.get('section_tags', []))}"
        )

    search = project.search(
        query=args.query,
        limit=5,
        channels=["entities", "facts", "communities"],
        include_graph_context=True,
    )
    print(
        f"search entities={len(search.entities)} facts={len(search.facts)} "
        f"communities={len(search.communities)} search_ms={search.search_ms}"
    )

    entities = project.entities.list(limit=5, type="component_instance")
    print(f"entities_list_count={len(entities)}")
    if entities:
        entity = project.entities.get(entities[0].id, include_invalid=False, expand_target=True)
        print(f"entity_get id={entity.id} label={entity.label} outgoing={len(entity.outgoing)}")

    relationships = project.relationships.list(limit=5, include_invalid=False)
    print(f"relationships_list_count={len(relationships)}")

    if args.cleanup:
        if target_sheet_id:
            deleted_sheet = project.sheets.delete(target_sheet_id)
            print(f"sheet_deleted={deleted_sheet.deleted} sheet_id={deleted_sheet.sheet_id}")

        deleted_project = fetched_project.delete()
        print(f"project_deleted={deleted_project.deleted} project_id={deleted_project.id}")
    else:
        print(f"kept_project_id={project.id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
