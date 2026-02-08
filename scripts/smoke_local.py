"""Local smoke test for StruAI Python SDK.

Usage:
  STRUAI_API_KEY=windowseat STRUAI_BASE_URL=http://localhost:8000 \
    python3 scripts/smoke_local.py

Optional:
  STRUAI_PDF=/path/to.pdf STRUAI_PAGE=12   # ingest sheet(s)
  STRUAI_SEARCH="GB18x18"                 # run search
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from struai import StruAI  # noqa: E402
from struai.resources.projects import JobBatch  # noqa: E402


def _wait_ingest(result_or_batch):
    if isinstance(result_or_batch, JobBatch):
        return result_or_batch.wait_all(timeout_per_job=300)
    return [result_or_batch.wait(timeout=300)]


def main() -> None:
    base_url = os.getenv("STRUAI_BASE_URL", "http://localhost:8000")
    api_key = os.getenv("STRUAI_API_KEY", "windowseat")
    client = StruAI(api_key=api_key, base_url=base_url)

    projects = client.projects.list(limit=1)
    if projects:
        project = client.projects.get(projects[0].id)
        created = False
    else:
        project = client.projects.create(name="Smoke Test Project")
        created = True

    entities = project.entities.list(limit=1)
    relationships = project.relationships.list(limit=1)
    print(f"project={project.id} entities={len(entities)} relationships={len(relationships)}")

    pdf_path = os.getenv("STRUAI_PDF")
    if pdf_path:
        page = os.getenv("STRUAI_PAGE", "1")
        ingest = project.sheets.add(pdf_path, page=page)
        results = _wait_ingest(ingest)
        print(f"ingested_jobs={len(results)} first_sheet_id={results[0].sheet_id}")

    search_query = os.getenv("STRUAI_SEARCH")
    if search_query:
        results = project.search(query=search_query, limit=3)
        print(
            "search entities="
            f"{len(results.entities)} "
            "facts="
            f"{len(results.facts)} "
            "communities="
            f"{len(results.communities)}"
        )

    if created:
        project.delete()


if __name__ == "__main__":
    main()
