#!/usr/bin/env python3
import os
import time
from pathlib import Path

from struai import StruAI

PDF_PATH = Path(
    "/Users/bhoshaga/PycharmProjects/windowseat/drawing_research/sample-pdf/structural-compiled.pdf"
)
PAGE = 12
BASE_URL = os.environ.get("STRUAI_BASE_URL", "https://api.stru.ai")


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

    job = project.sheets.add(page=PAGE, file_hash=file_hash)
    status = job.status()
    print(f"job_id={job.id} status={status.status}")
    sheet_result = job.wait(timeout=180)
    print(
        f"sheet_id={sheet_result.sheet_id} "
        f"entities_created={sheet_result.entities_created} "
        f"relationships_created={sheet_result.relationships_created}"
    )

    sheets = project.sheets.list(limit=5)
    print(f"sheets_list_count={len(sheets)}")
    sheet = project.sheets.get(sheet_result.sheet_id)
    print(f"sheet_get_id={sheet.id} page={sheet.page}")

    search = project.search(
        query="beam connection",
        limit=5,
        include_graph_context=True,
    )
    print(f"search_results={len(search.results)} search_ms={search.search_ms}")
    if search.results:
        top = search.results[0]
        print(f"search_top={top.entity.label} score={top.score}")

    answer = project.query("What beams are called out on this sheet?")
    print(f"query_answer={answer.answer} confidence={answer.confidence}")

    entities = project.entities.list(limit=3)
    print(f"entities_list_count={len(entities)}")
    if entities:
        entity = project.entities.get(entities[0].id)
        print(f"entity_get_id={entity.id} label={entity.label}")

    relationships = project.relationships.list(limit=3)
    print(f"relationships_list_count={len(relationships)}")

    print("\nDone. Project retained for inspection:", project.id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
