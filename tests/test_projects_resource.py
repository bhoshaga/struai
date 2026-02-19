from __future__ import annotations

from typing import Any

from struai.models.projects import JobStatus
from struai.resources.projects import Job, JobBatch, ProjectInstance


def _cypher_payload(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ok": True,
        "records": records,
    }


class FakeClient:
    def __init__(self) -> None:
        self.status_calls = 0
        self.cypher_calls = 0

    def get(self, path: str, params: dict[str, Any] | None = None, cast_to=None):
        if path.startswith("/projects/proj/jobs/"):
            self.status_calls += 1
            payload = {
                "job_id": path.split("/")[-1],
                "status": "complete",
                "result": {
                    "sheet_id": f"sheet_{self.status_calls}",
                    "entities_created": 10,
                    "relationships_created": 20,
                },
                "status_log": [],
                "step_timings": {},
            }
            return cast_to.model_validate(payload) if cast_to else payload

        if path == "/projects/proj/search":
            payload = {
                "ok": True,
                "hits": [{"node": {"properties": {"uuid": "node_1"}}, "score": 0.9}],
            }
            return cast_to.model_validate(payload) if cast_to else payload

        raise AssertionError(f"unexpected GET {path}")

    def post(self, path: str, *, files=None, data=None, json=None, cast_to=None):
        if path == "/projects/proj/sheets":
            page_selector = str((data or {}).get("page"))
            if page_selector == "1":
                payload = {"jobs": [{"job_id": "job_single", "page": 1}]}
            else:
                payload = {
                    "jobs": [
                        {"job_id": "job_a", "page": 1},
                        {"job_id": "job_b", "page": 2},
                    ]
                }
            return cast_to.model_validate(payload) if cast_to else payload

        if path == "/projects/proj/cypher":
            self.cypher_calls += 1
            if self.cypher_calls == 1:
                payload = _cypher_payload([])
            elif self.cypher_calls == 2:
                payload = _cypher_payload([{"label": "Callout", "count": 2}])
            elif self.cypher_calls == 3:
                payload = _cypher_payload([{"rel_type": "REFERENCES", "count": 5}])
            elif self.cypher_calls == 4:
                payload = _cypher_payload(
                    [
                        {
                            "has_sheet_node": False,
                            "sheet_node_count": 0,
                            "non_sheet_total": 3,
                            "reachable_non_sheet": 1,
                        }
                    ]
                )
            elif self.cypher_calls == 5:
                payload = _cypher_payload(
                    [{"uuid": "u1", "labels": ["Callout"], "category": "callout", "name": "A"}]
                )
            else:
                raise AssertionError("unexpected cypher call count")
            return cast_to.model_validate(payload) if cast_to else payload

        raise AssertionError(f"unexpected POST {path}")

    def delete(self, path: str, *, cast_to=None):
        payload = {
            "deleted": True,
            "project_id": "proj",
            "projects_deleted": 1,
            "nodes_deleted": 0,
            "relationships_deleted": 0,
            "owner_mapping_deleted": True,
            "qdrant_deleted_points": 0,
        }
        return cast_to.model_validate(payload) if cast_to else payload


def test_single_page_ingest_returns_job() -> None:
    client = FakeClient()
    project = ProjectInstance(client, cast_to_project())

    ingest = project.sheets.add(page=1, file_hash="abc123")
    assert isinstance(ingest, Job)

    status = ingest.status()
    assert isinstance(status, JobStatus)
    assert status.is_complete

    result = ingest.wait(timeout=5, poll_interval=0)
    assert result.sheet_id == "sheet_2"
    assert result.entities_created == 10


def test_multi_page_ingest_returns_batch() -> None:
    client = FakeClient()
    project = ProjectInstance(client, cast_to_project())

    ingest = project.sheets.add(page="1,2", file_hash="abc123")
    assert isinstance(ingest, JobBatch)
    assert ingest.ids == ["job_a", "job_b"]

    results = ingest.wait_all(timeout_per_job=5, poll_interval=0)
    assert len(results) == 2
    assert results[0].sheet_id is not None
    assert results[1].sheet_id is not None


def test_docquery_search_parses_payload() -> None:
    client = FakeClient()
    project = ProjectInstance(client, cast_to_project())

    response = project.docquery.search("beam", limit=10)
    assert len(response.hits) == 1
    assert response.hits[0].score == 0.9
    assert response.hits[0].node["properties"]["uuid"] == "node_1"


def test_docquery_sheet_summary_returns_warning_payload() -> None:
    client = FakeClient()
    project = ProjectInstance(client, cast_to_project())

    response = project.docquery.sheet_summary("S111", orphan_limit=5)

    assert response.command == "sheet-summary"
    assert response.reachability["has_sheet_node"] is False
    assert response.reachability["unreachable_non_sheet"] == 2
    warning_types = {w["type"] for w in response.warnings}
    assert "missing_sheet_node" in warning_types
    assert "unreachable_entities" in warning_types
    assert len(response.orphan_examples) == 1


def cast_to_project():
    from struai.models.projects import Project

    return Project.model_validate({"id": "proj", "name": "Smoke"})
