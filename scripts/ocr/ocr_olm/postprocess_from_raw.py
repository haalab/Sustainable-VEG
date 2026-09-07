# SPDX-License-Identifier: Apache-2.0
"""Recover olmOCR output.json files from saved raw responses and metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def convert_bbox(bbox: object, page_width: float, page_height: float, render_width: int, render_height: int) -> list[float] | None:
    if not isinstance(bbox, list) or len(bbox) != 4:
        return None
    try:
        x1, y1, x2, y2 = map(float, bbox)
    except (TypeError, ValueError):
        return None
    x1, x2 = sorted((x1 * page_width / render_width, x2 * page_width / render_width))
    y1, y2 = sorted((y1 * page_height / render_height, y2 * page_height / render_height))
    x1, x2 = max(0.0, x1), min(page_width, x2)
    y1, y2 = max(0.0, y1), min(page_height, y2)
    return [x1, y1, x2, y2] if x2 - x1 >= 1 and y2 - y1 >= 1 else None


def draw_preview(report_path: Path, page_number: int, objects: list[dict], output_path: Path) -> None:
    with fitz.open(report_path) as document:
        pixmap = document[page_number - 1].get_pixmap(alpha=False)
    image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    draw = ImageDraw.Draw(image)
    for item in objects:
        bbox = item.get("bbox_pdf")
        if isinstance(bbox, list) and len(bbox) == 4:
            draw.rectangle(tuple(bbox), outline="red", width=2)
    image.save(output_path)


def process_page(page_dir: Path, reports_dir: Path, overwrite: bool = False) -> bool:
    raw_path = page_dir / "output_raw.txt"
    metadata_path = page_dir / "meta.json"
    output_path = page_dir / "output.json"
    if output_path.exists() and not overwrite:
        return False
    if not raw_path.is_file() or not metadata_path.is_file():
        return False

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    data = json.loads(raw_path.read_text(encoding="utf-8"))
    objects = data.get("objects", [])
    if not isinstance(objects, list):
        objects = []

    valid_objects = []
    for item in objects:
        if not isinstance(item, dict):
            continue
        bbox_pdf = convert_bbox(
            item.get("bbox"),
            float(metadata["page_width"]),
            float(metadata["page_height"]),
            int(metadata["render_w"]),
            int(metadata["render_h"]),
        )
        if bbox_pdf is None:
            continue
        item["bbox_pdf"] = bbox_pdf
        valid_objects.append(item)

    data["objects"] = valid_objects
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    report_path = reports_dir / f"{page_dir.parent.name}.pdf"
    if report_path.is_file():
        draw_preview(report_path, int(page_dir.name), valid_objects, page_dir / "bbox.png")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ocr-root",
        type=Path,
        default=PROJECT_ROOT / "artifacts" / "ocr" / "olm",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "reports",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    processed = 0
    for raw_path in sorted(args.ocr_root.glob("*/*/output_raw.txt")):
        try:
            processed += process_page(raw_path.parent, args.reports_dir, args.overwrite)
        except (json.JSONDecodeError, KeyError, ValueError) as error:
            print(f"[WARN] {raw_path.parent}: {error}")
    print(f"Processed {processed} page(s).")


if __name__ == "__main__":
    main()
