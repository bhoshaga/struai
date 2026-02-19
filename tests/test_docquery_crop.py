from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import pytest

from struai.resources.projects import ProjectInstance


class CropClient:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, cast_to=None):
        raise AssertionError(f"unexpected GET {path}")

    def post(
        self, path: str, *, files=None, data=None, json=None, cast_to=None, expect_bytes=False
    ):
        if path != "/projects/proj/crop":
            raise AssertionError(f"unexpected POST {path}")

        self.requests.append({"path": path, "json": json, "expect_bytes": expect_bytes})
        if not expect_bytes:
            raise AssertionError("crop endpoint should request binary response")

        # Minimal PNG header + payload bytes for smoke testing file write path.
        return b"\x89PNG\r\n\x1a\nstruai-test-crop"

    def delete(self, path: str, *, cast_to=None):
        raise AssertionError(f"unexpected DELETE {path}")


def _project_instance(client: Any) -> ProjectInstance:
    from struai.models.projects import Project

    project = Project.model_validate({"id": "proj", "name": "Crop Tests"})
    return ProjectInstance(client, project)


def test_crop_bbox_mode_posts_to_server_and_writes_output(tmp_path: Path) -> None:
    output_path = tmp_path / "crop.png"
    client = CropClient()
    project = _project_instance(client)

    result = project.docquery.crop(
        output=output_path,
        bbox=[10, 20, 30, 45],
        page_hash="page_hash_1",
    )

    assert output_path.exists()
    assert output_path.read_bytes().startswith(b"\x89PNG")
    assert result.ok is True
    assert result.output_path == str(output_path)
    assert result.bytes_written > 0
    assert result.content_type == "image/png"

    assert len(client.requests) == 1
    request = client.requests[0]
    assert request["expect_bytes"] is True
    assert request["json"]["bbox"] == [10.0, 20.0, 30.0, 45.0]
    assert request["json"]["page_hash"] == "page_hash_1"


def test_crop_uuid_mode_posts_uuid_only(tmp_path: Path) -> None:
    output_path = tmp_path / "crop_uuid.png"
    client = CropClient()
    project = _project_instance(client)

    result = project.docquery.crop(output=output_path, uuid="node-123")

    assert output_path.exists()
    assert result.bytes_written > 0
    assert len(client.requests) == 1
    assert client.requests[0]["json"] == {"uuid": "node-123"}


def test_crop_bbox_requires_page_hash(tmp_path: Path) -> None:
    output_path = tmp_path / "crop_fail.png"
    client = CropClient()
    project = _project_instance(client)

    with pytest.raises(ValueError, match="page_hash"):
        project.docquery.crop(output=output_path, bbox=[1, 2, 3, 4])
