#!/usr/bin/env python3
"""Portable end-to-end Tier 1 + Tier 2 projects/docquery SDK workflow example."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Any, List, Optional

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
        help="DocQuery search text after ingestion",
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
    parser.add_argument(
        "--crop-output",
        default=os.environ.get("STRUAI_CROP_OUTPUT", "sdk_crop.png"),
        help="Output PNG path for server-side docquery.crop demo (default: sdk_crop.png)",
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


def _first_hit_uuid(search_payload: Any) -> Optional[str]:
    for hit in search_payload.hits:
        node = hit.node or {}
        uuid = node.get("properties", {}).get("uuid")
        if uuid:
            return str(uuid)
    return None


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

    print("\n== Tier 2: Projects + DocQuery ==")
    project_name = f"SDK Workflow {int(time.time())}"
    project = client.projects.create(
        name=project_name,
        description=f"Created from {pdf_path.name} page {args.page}",
    )
    print(f"project_created id={project.id} name={project.name}")

    projects: List[Any] = client.projects.list()
    print(f"projects_list_count={len(projects)}")

    opened_project = client.projects.open(project.id)
    print(f"project_open id={opened_project.id} name={opened_project.name}")

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

    if not sheet_result.sheet_id:
        print("No sheet_id returned from ingest; skipping sheet-scoped docquery calls.")
        target_sheet_id = None
    else:
        target_sheet_id = sheet_result.sheet_id

    if target_sheet_id:
        sheet_entities = project.docquery.sheet_entities(target_sheet_id, limit=20)
        print(f"sheet_entities_count={len(sheet_entities.entities)}")

        sheet_summary = project.docquery.sheet_summary(target_sheet_id, orphan_limit=10)
        print(
            "sheet_summary "
            f"unreachable_non_sheet={sheet_summary.reachability.get('unreachable_non_sheet', 0)} "
            f"warnings={len(sheet_summary.warnings)}"
        )

    sheet_list = project.docquery.sheet_list()
    print(
        "sheet_list "
        f"sheet_node_count={sheet_list.totals.get('sheet_node_count', 0)} "
        f"mismatch_warnings={len(sheet_list.mismatch_warnings)}"
    )

    search = project.docquery.search(args.query, limit=5)
    print(f"docquery_search_count={len(search.hits)}")

    first_uuid = _first_hit_uuid(search)
    if first_uuid:
        node_payload = project.docquery.node_get(first_uuid)
        print(f"node_get_found={node_payload.found} uuid={first_uuid}")

        neighbors = project.docquery.neighbors(
            first_uuid,
            mode="both",
            direction="both",
            radius=200.0,
            limit=10,
        )
        print(f"neighbors_count={len(neighbors.neighbors)}")

        resolved = project.docquery.reference_resolve(first_uuid, limit=10)
        print(
            f"reference_resolve_found={resolved.found} "
            f"resolved_count={resolved.count} warnings={len(resolved.warnings)}"
        )

        crop = project.docquery.crop(
            uuid=first_uuid,
            output=args.crop_output,
        )
        print(
            "crop "
            f"path={crop.output_path} "
            f"bytes_written={crop.bytes_written} "
            f"content_type={crop.content_type}"
        )
    else:
        print("No search hit UUID found; skipping node/neighbors/reference-resolve.")

    cypher = project.docquery.cypher(
        "MATCH (n:Entity {project_id:$project_id}) RETURN count(n) AS total_entities",
        max_rows=1,
    )
    total_entities = cypher.records[0].get("total_entities") if cypher.records else 0
    print(f"cypher_total_entities={total_entities}")

    if args.cleanup:
        if target_sheet_id:
            deleted_sheet = project.sheets.delete(target_sheet_id)
            print(f"sheet_deleted={deleted_sheet.deleted} sheet_id={deleted_sheet.sheet_id}")

        deleted_project = opened_project.delete()
        print(f"project_deleted={deleted_project.deleted} project_id={deleted_project.project_id}")
    else:
        print(f"kept_project_id={project.id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
