#!/usr/bin/env python3
"""Runnable Page 12 cookbook example.

Usage:
  export STRUAI_API_KEY=YOUR_API_KEY
  export STRUAI_BASE_URL=https://api.stru.ai
  python3 examples/page12_cookbook.py

Optional:
  export STRUAI_PROJECT_ID=proj_86c0f02e
  export STRUAI_SHEET_ID=S111
  export STRUAI_QUERY="section S311"
  export STRUAI_CROP_OUTPUT=/tmp/page12_crop_from_uuid.png
"""

from __future__ import annotations

import os
import time
from typing import Any, Callable, Sequence, TypeVar

from struai import APIError, StruAI

T = TypeVar("T")


def _env_required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing {name}")
    return value


def _is_transient(exc: APIError) -> bool:
    if exc.status_code in {502, 503, 504}:
        return True
    return str(exc.code or "").lower() in {"drawing_warming_up", "drawing_unavailable"}


def _call_with_retry(fn: Callable[[], T], *, label: str, attempts: int = 4) -> T:
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except APIError as exc:
            if _is_transient(exc) and attempt < attempts:
                wait_s = min(2 ** (attempt - 1), 8)
                print(
                    f"{label}_retry attempt={attempt} wait_s={wait_s} "
                    f"status={exc.status_code} code={exc.code}"
                )
                time.sleep(wait_s)
                continue
            raise
    raise RuntimeError(f"{label} failed after retries")


def _pick_project(projects: Sequence[Any], preferred_project_id: str) -> Any:
    if not projects:
        raise SystemExit(
            "No accessible projects found for this API key. "
            "Create/ingest a project first, then rerun."
        )
    for project in projects:
        if getattr(project, "id", None) == preferred_project_id:
            return project
    return projects[0]


def _pick_sheet_id(sheet_nodes: Sequence[dict[str, Any]], preferred_sheet_id: str) -> str:
    if not sheet_nodes:
        raise SystemExit(
            "Selected project has no sheet nodes yet. Ingest at least one sheet, then rerun."
        )

    ids = [str(node.get("sheet_id")) for node in sheet_nodes if node.get("sheet_id")]
    if not ids:
        raise SystemExit("sheet_list returned no usable sheet_id values.")
    if preferred_sheet_id in ids:
        return preferred_sheet_id
    return ids[0]


def main() -> int:
    api_key = _env_required("STRUAI_API_KEY")
    base_url = _env_required("STRUAI_BASE_URL")

    preferred_project_id = os.getenv("STRUAI_PROJECT_ID", "proj_86c0f02e")
    preferred_sheet_id = os.getenv("STRUAI_SHEET_ID", "S111")
    query_text = os.getenv("STRUAI_QUERY", "section S311")
    crop_output = os.getenv("STRUAI_CROP_OUTPUT", "/tmp/page12_crop_from_uuid.png")

    client = StruAI(api_key=api_key, base_url=base_url)

    projects = _call_with_retry(client.projects.list, label="projects_list")
    print("project_count:", len(projects))

    selected = _pick_project(projects, preferred_project_id)
    project_id = str(getattr(selected, "id"))
    project = client.projects.open(project_id, name=getattr(selected, "name", None))
    print("project_id:", project_id)

    sheet_list = _call_with_retry(project.docquery.sheet_list, label="sheet_list")
    print("sheet_nodes:", len(sheet_list.sheet_nodes))

    sheet_id = _pick_sheet_id(sheet_list.sheet_nodes, preferred_sheet_id)
    print("sheet_id:", sheet_id)

    sheet_summary = _call_with_retry(
        lambda: project.docquery.sheet_summary(sheet_id, orphan_limit=10),
        label="sheet_summary",
    )
    print("unreachable:", sheet_summary.reachability.get("unreachable_non_sheet", 0))

    entities = _call_with_retry(
        lambda: project.docquery.sheet_entities(sheet_id, limit=20),
        label="sheet_entities",
    )
    print("entities_count:", len(entities.entities))

    search = _call_with_retry(
        lambda: project.docquery.search(query_text, limit=5),
        label="search",
    )
    print("search_count:", len(search.hits))

    cypher = _call_with_retry(
        lambda: project.docquery.cypher(
            "MATCH (n:Entity {project_id:$project_id, sheet_id:$sheet_id}) "
            "WHERE NOT n:Sheet AND NOT n:Zone "
            "  AND n.bbox_min IS NOT NULL AND n.bbox_max IS NOT NULL "
            "RETURN n.uuid AS uuid, n.page_hash AS page_hash "
            "ORDER BY (n.bbox_max.x - n.bbox_min.x) * (n.bbox_max.y - n.bbox_min.y) "
            "LIMIT 1",
            params={"sheet_id": sheet_id},
            max_rows=1,
        ),
        label="cypher",
    )
    print("cypher_rows:", len(cypher.records))
    if not cypher.records:
        raise SystemExit("No bbox-capable node found for this sheet.")

    node_uuid = str(cypher.records[0]["uuid"])

    node = _call_with_retry(
        lambda: project.docquery.node_get(node_uuid),
        label="node_get",
    )
    print("node_found:", node.found, "uuid:", node_uuid)

    neighbors = _call_with_retry(
        lambda: project.docquery.neighbors(
            node_uuid,
            mode="both",
            direction="both",
            radius=200.0,
            limit=10,
        ),
        label="neighbors",
    )
    print("neighbors_count:", len(neighbors.neighbors))

    resolved = _call_with_retry(
        lambda: project.docquery.reference_resolve(node_uuid, limit=20),
        label="reference_resolve",
    )
    print("reference_count:", resolved.count, "warnings:", len(resolved.warnings))

    crop_uuid = _call_with_retry(
        lambda: project.docquery.crop(
            uuid=node_uuid,
            output=crop_output,
        ),
        label="crop",
    )
    print("crop_uuid:", crop_uuid.output_path, crop_uuid.bytes_written, crop_uuid.content_type)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
