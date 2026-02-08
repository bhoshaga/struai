#!/usr/bin/env python3
import os
import time
from pathlib import Path

from struai import StruAI
from struai.resources.projects import JobBatch

PDF_PATH = Path(
    "/Users/bhoshaga/PycharmProjects/windowseat/drawing_research/sample-pdf/structural-compiled.pdf"
)
PAGE = 12
BASE_URL = os.environ.get("STRUAI_BASE_URL", "https://api.stru.ai")


def _wait_ingest(result_or_batch):
    if isinstance(result_or_batch, JobBatch):
        return result_or_batch.wait_all(timeout_per_job=180)[0]
    return result_or_batch.wait(timeout=180)


def main() -> int:
    api_key = os.environ.get("STRUAI_API_KEY")
    if not api_key:
        print("Missing STRUAI_API_KEY. Get an API key from stru.ai.")
        return 1

    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}")
        return 1

    client = StruAI(api_key=api_key, base_url=BASE_URL)

    print("== Tier 1: Raw Detection ==")
    file_hash = client.drawings.compute_file_hash(PDF_PATH)
    print(f"file_hash={file_hash}")

    result = client.drawings.analyze(page=PAGE, file_hash=file_hash)
    print(f"drawing_id={result.id} processing_ms={result.processing_ms}")
    print(
        "leaders="
        f"{len(result.annotations.leaders)} "
        "section_tags="
        f"{len(result.annotations.section_tags)} "
        "detail_tags="
        f"{len(result.annotations.detail_tags)}"
    )

    fetched = client.drawings.get(result.id)
    print(f"drawing_get_id={fetched.id} page={fetched.page}")

    print("\n== Tier 2: Graph + Search ==")
    project_name = f"Page12 Test {int(time.time())}"
    project = client.projects.create(
        name=project_name,
        description="SDK full test for structural-compiled.pdf page 12",
    )
    print(f"project_id={project.id} name={project.name}")

    projects = client.projects.list(limit=3)
    print(f"projects_list_count={len(projects)}")

    ingest = project.sheets.add(page=PAGE, file_hash=file_hash)
    sheet_result = _wait_ingest(ingest)
    print(
        f"sheet_id={sheet_result.sheet_id} "
        f"entities_created={sheet_result.entities_created} "
        f"relationships_created={sheet_result.relationships_created}"
    )

    sheets = project.sheets.list(limit=5)
    print(f"sheets_list_count={len(sheets)}")
    sheet = project.sheets.get(sheet_result.sheet_id)
    print(f"sheet_get_id={sheet.id} page={sheet.page}")

    raw = project.sheets.get_annotations(sheet_result.sheet_id)
    print(f"sheet_annotations_leaders={len(raw.annotations.get('leaders', []))}")

    search = project.search(
        query="beam connection",
        limit=5,
        include_graph_context=True,
    )
    print(
        "search_entities="
        f"{len(search.entities)} "
        "facts="
        f"{len(search.facts)} "
        "communities="
        f"{len(search.communities)} "
        f"search_ms={search.search_ms}"
    )
    if search.entities:
        top = search.entities[0]
        print(f"search_top={top.label} score={top.score}")

    entities = project.entities.list(limit=3)
    print(f"entities_list_count={len(entities)}")
    if entities:
        entity = project.entities.get(entities[0].id, expand_target=True)
        print(f"entity_get_id={entity.id} label={entity.label}")

    relationships = project.relationships.list(limit=3)
    print(f"relationships_list_count={len(relationships)}")

    print("\nDone. Project retained for inspection:", project.id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
