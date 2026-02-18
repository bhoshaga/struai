from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

from struai.resources.projects import ProjectInstance


def _cypher_payload(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ok": True,
        "command": "cypher",
        "input": {},
        "records": records,
        "record_count": len(records),
        "truncated": False,
        "summary": {},
    }


class CropClient:
    def __init__(self, *, include_node: bool = False):
        self.include_node = include_node
        self.node_get_calls = 0
        self.cypher_calls = 0

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, cast_to=None):
        if path == "/projects/proj/docquery/node-get" and self.include_node:
            self.node_get_calls += 1
            payload = {
                "ok": True,
                "command": "node-get",
                "input": {"uuid": (params or {}).get("uuid")},
                "found": True,
                "node": {
                    "properties": {
                        "uuid": (params or {}).get("uuid"),
                        "page_hash": "page_hash_1",
                        "sheet_id": "S111",
                        "name": "Target Node",
                        "category": "callout",
                        "bbox_min": {"x": 10, "y": 20},
                        "bbox_max": {"x": 110, "y": 70},
                    }
                },
                "summary": {},
            }
            return cast_to.model_validate(payload) if cast_to else payload
        raise AssertionError(f"unexpected GET {path}")

    def post(self, path: str, *, files=None, data=None, json=None, cast_to=None):
        if path == "/projects/proj/docquery/cypher" and self.include_node:
            self.cypher_calls += 1
            payload = _cypher_payload([{"min_x": 0, "min_y": 0, "max_x": 200, "max_y": 100}])
            return cast_to.model_validate(payload) if cast_to else payload
        raise AssertionError(f"unexpected POST {path}")

    def delete(self, path: str, *, cast_to=None):
        raise AssertionError(f"unexpected DELETE {path}")


def _project_instance(client: Any) -> ProjectInstance:
    from struai.models.projects import Project

    project = Project.model_validate({"id": "proj", "name": "Crop Tests"})
    return ProjectInstance(client, project)


def test_crop_bbox_mode_writes_output(tmp_path: Path) -> None:
    image_path = tmp_path / "source.png"
    output_path = tmp_path / "crop.png"
    Image.new("RGB", (100, 80), color="white").save(image_path)

    project = _project_instance(CropClient(include_node=False))
    result = project.docquery.crop(
        output=output_path,
        bbox=[10, 20, 30, 45],
        image=image_path,
    )

    assert output_path.exists()
    assert result.command == "crop"
    assert result.source["mode"] == "bbox"
    assert result.output_image["width"] == 20
    assert result.output_image["height"] == 25
    assert result.transform["scale_mode"] == "identity"


def test_crop_uuid_mode_auto_scales_using_page_extents(tmp_path: Path) -> None:
    image_path = tmp_path / "source.png"
    output_path = tmp_path / "crop_uuid.png"
    Image.new("RGB", (400, 200), color="white").save(image_path)

    client = CropClient(include_node=True)
    project = _project_instance(client)
    result = project.docquery.crop(
        output=output_path,
        uuid="node-123",
        image=image_path,
        auto_scale=True,
    )

    assert output_path.exists()
    assert client.node_get_calls == 1
    assert client.cypher_calls == 1
    assert result.source["mode"] == "uuid"
    assert result.source["uuid"] == "node-123"
    assert result.output_image["width"] == 200
    assert result.output_image["height"] == 100
    assert result.transform["scale_mode"] == "auto_page_extents"
