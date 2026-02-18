# Page 12 Cookbook (Python + JS)

This cookbook shows end-to-end DocQuery traversal on structural page 12, including `cypher` and image `crop`.

## Target Context

- PDF: `/Users/bhoshaga/PycharmProjects/stru/drawing_pipeline/sample-pdf/structural-compiled.pdf`
- Page: `12`
- Typical project used in QC: `proj_86c0f02e`
- Typical sheet on page 12: `S111`
- Example cached page image for crop:
  - `/Users/bhoshaga/PycharmProjects/stru/drawing_pipeline/cache/66b98c7019417252/step2b/page_context.png`

## Install

```bash
pip install struai
npm install struai
```

## Environment

```bash
export STRUAI_API_KEY=windowseat
export STRUAI_BASE_URL=https://api.stru.ai
```

## Python: All 10 Operations

```python
from pathlib import Path
from struai import StruAI

client = StruAI(api_key="windowseat", base_url="https://api.stru.ai")
project = client.projects.open("proj_86c0f02e")
sheet_id = "S111"

# 1) project-list
projects = client.projects.list()
print("project_count:", len(projects))

# 2) sheet-list
sheet_list = project.docquery.sheet_list()
print("sheet_nodes:", len(sheet_list.sheet_nodes))

# 3) sheet-summary
sheet_summary = project.docquery.sheet_summary(sheet_id, orphan_limit=10)
print("unreachable:", sheet_summary.reachability.get("unreachable_non_sheet", 0))

# 4) sheet-entities
entities = project.docquery.sheet_entities(sheet_id, limit=20)
print("entities_count:", entities.count)

# 5) search
search = project.docquery.search("section S311", limit=5)
print("search_count:", search.count)

# 6) cypher (custom query string + params)
cypher = project.docquery.cypher(
    "MATCH (n:Entity {project_id:$project_id, sheet_id:$sheet_id}) "
    "WHERE n.bbox_min IS NOT NULL AND n.bbox_max IS NOT NULL "
    "RETURN n.uuid AS uuid, n.page_hash AS page_hash LIMIT 1",
    params={"sheet_id": sheet_id},
    max_rows=1,
)
print("cypher_rows:", cypher.record_count)

if not cypher.records:
    raise RuntimeError("No bbox-capable node found for this sheet")

node_uuid = str(cypher.records[0]["uuid"])

# 7) node-get
node = project.docquery.node_get(node_uuid)
print("node_found:", node.found, "uuid:", node_uuid)

# 8) neighbors
neighbors = project.docquery.neighbors(node_uuid, direction="both", limit=10)
print("neighbors_count:", neighbors.count)

# 9) reference-resolve
resolved = project.docquery.reference_resolve(node_uuid, limit=20)
print("reference_count:", resolved.count, "warnings:", len(resolved.warnings))

# 10) crop (uuid mode)
crop_uuid = project.docquery.crop(
    uuid=node_uuid,
    image="/Users/bhoshaga/PycharmProjects/stru/drawing_pipeline/cache/66b98c7019417252/step2b/page_context.png",
    output="/tmp/page12_crop_from_uuid.png",
)
print("crop_uuid:", crop_uuid.output_image["path"], crop_uuid.output_image["width"], crop_uuid.output_image["height"])

# Optional: crop (bbox mode)
crop_bbox = project.docquery.crop(
    bbox=[1000, 700, 1400, 980],
    image="/Users/bhoshaga/PycharmProjects/stru/drawing_pipeline/cache/66b98c7019417252/step2b/page_context.png",
    output="/tmp/page12_crop_from_bbox.png",
)
print("crop_bbox:", crop_bbox.output_image["path"], crop_bbox.output_image["width"], crop_bbox.output_image["height"])
```

## JavaScript: Core Traversal + Cypher + Crop

```js
import { StruAI } from "struai";

const client = new StruAI({
  apiKey: process.env.STRUAI_API_KEY || "windowseat",
  baseUrl: process.env.STRUAI_BASE_URL || "https://api.stru.ai",
});

const project = client.projects.open("proj_86c0f02e");
const sheetId = "S111";

const projects = await client.projects.list();
console.log("project_count:", projects.length);

const summary = await project.docquery.sheetSummary(sheetId, { orphanLimit: 10 });
console.log("unreachable:", summary.reachability.unreachable_non_sheet ?? 0);

const cypher = await project.docquery.cypher(
  "MATCH (n:Entity {project_id:$project_id, sheet_id:$sheet_id}) " +
    "WHERE n.bbox_min IS NOT NULL AND n.bbox_max IS NOT NULL " +
    "RETURN n.uuid AS uuid LIMIT 1",
  { params: { sheet_id: sheetId }, maxRows: 1 },
);

const uuid = String(cypher.records[0].uuid);
const crop = await project.docquery.crop({
  uuid,
  image: "/Users/bhoshaga/PycharmProjects/stru/drawing_pipeline/cache/66b98c7019417252/step2b/page_context.png",
  output: "/tmp/page12_crop_js.png",
});

console.log("crop:", crop.output_image.path, crop.output_image.width, crop.output_image.height);
```

## Notes

- The SDK default base URL is `https://api.stru.ai`.
- `client.projects.list()` is the SDK equivalent of CLI `project-list`.
- The remaining CLI-equivalent operations are under `project.docquery.*`.
