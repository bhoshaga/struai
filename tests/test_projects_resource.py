from __future__ import annotations

from typing import Any

from struai.models.projects import JobStatus
from struai.resources.projects import Job, JobBatch, ProjectInstance


class FakeClient:
    def __init__(self) -> None:
        self.status_calls = 0

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
        raise AssertionError(f"unexpected GET {path}")

    def post(self, path: str, *, files=None, data=None, json=None, cast_to=None):
        if path == "/projects/proj/search":
            payload = {
                "entities": [{"id": "e1", "type": "mention", "score": 0.9}],
                "facts": [{"id": "f1", "score": 0.8}],
                "communities": [{"id": "c1", "score": 0.7}],
                "search_ms": 42,
            }
            return cast_to.model_validate(payload) if cast_to else payload

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

        raise AssertionError(f"unexpected POST {path}")

    def delete(self, path: str, *, cast_to=None):
        payload = {"deleted": True, "id": path.split("/")[-1]}
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


def test_project_search_parses_channel_payload() -> None:
    client = FakeClient()
    project = ProjectInstance(client, cast_to_project())

    response = project.search("beam", channels=["entities", "facts"], include_graph_context=True)
    assert response.search_ms == 42
    assert len(response.entities) == 1
    assert len(response.facts) == 1
    assert len(response.communities) == 1


def cast_to_project():
    from struai.models.projects import Project

    return Project.model_validate({"id": "proj", "name": "Smoke"})
