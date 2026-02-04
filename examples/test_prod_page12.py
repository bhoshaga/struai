#!/usr/bin/env python3
import os
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

    result = client.drawings.analyze(str(PDF_PATH), page=PAGE)
    print(f"Processed in {result.processing_ms}ms")
    print(
        "leaders="
        f"{len(result.annotations.leaders)} "
        "section_tags="
        f"{len(result.annotations.section_tags)} "
        "detail_tags="
        f"{len(result.annotations.detail_tags)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
