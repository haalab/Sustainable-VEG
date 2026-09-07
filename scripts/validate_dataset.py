# SPDX-License-Identifier: Apache-2.0
"""Validate Sustainable-VEG annotation structure and print a compact summary."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = PROJECT_ROOT / "data" / "Sustainable-VEG.json"
BOX_PATTERN = re.compile(
    r"^(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),"
    r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?):([^:]+)$"
)
REQUIRED_KEYS = {"id", "page", "label", "company", "esg_report", "sasb_report"}


def _safe_relative_path(value: object, field: str, sample_id: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{sample_id}: {field} must be a non-empty string")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{sample_id}: {field} must be a safe relative path")
    return path


def validate(path: Path, check_reports: bool = False) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list):
        raise ValueError("Dataset root must be a JSON array")

    seen_ids: set[str] = set()
    companies: Counter[str] = Counter()
    industries: Counter[str] = Counter()
    positive_pages = 0
    box_count = 0
    missing_reports: set[str] = set()

    for position, item in enumerate(records):
        if not isinstance(item, dict):
            raise ValueError(f"Record {position} must be a JSON object")
        missing = REQUIRED_KEYS - item.keys()
        if missing:
            raise ValueError(f"Record {position} is missing keys: {sorted(missing)}")

        sample_id = item["id"]
        if not isinstance(sample_id, str) or not sample_id:
            raise ValueError(f"Record {position}: id must be a non-empty string")
        if sample_id in seen_ids:
            raise ValueError(f"Duplicate sample id: {sample_id}")
        seen_ids.add(sample_id)

        if not isinstance(item["page"], int) or item["page"] < 1:
            raise ValueError(f"{sample_id}: page must be a positive integer")
        if not isinstance(item["company"], str) or not item["company"]:
            raise ValueError(f"{sample_id}: company must be a non-empty string")
        companies[item["company"]] += 1

        report_path = _safe_relative_path(item["esg_report"], "esg_report", sample_id)
        sasb_path = _safe_relative_path(item["sasb_report"], "sasb_report", sample_id)
        industry = sasb_path.stem.removeprefix("SASB-")
        industries[industry] += 1

        labels = item["label"]
        if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
            raise ValueError(f"{sample_id}: label must be an array of strings")
        positive_pages += bool(labels)
        box_count += len(labels)
        for label in labels:
            match = BOX_PATTERN.fullmatch(label.strip())
            if not match:
                raise ValueError(f"{sample_id}: invalid label '{label}'")
            x1, y1, x2, y2 = map(float, match.groups()[:4])
            code = match.group(5).strip()
            if min(x1, y1, x2, y2) < 0 or not (x1 < x2 and y1 < y2):
                raise ValueError(f"{sample_id}: invalid coordinates in '{label}'")
            if not code.startswith(f"{industry}-"):
                raise ValueError(f"{sample_id}: metric '{code}' does not match industry '{industry}'")

        if check_reports:
            local_report = PROJECT_ROOT / "data" / "reports" / report_path.name
            if not local_report.is_file():
                missing_reports.add(report_path.name)

    if missing_reports:
        names = ", ".join(sorted(missing_reports))
        raise FileNotFoundError(f"Missing {len(missing_reports)} report PDFs: {names}")

    return {
        "records": len(records),
        "positive_pages": positive_pages,
        "evidence_boxes": box_count,
        "companies": len(companies),
        "industries": len(industries),
        "pages_by_industry": dict(sorted(industries.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", nargs="?", type=Path, default=DEFAULT_DATASET)
    parser.add_argument(
        "--check-reports",
        action="store_true",
        help="also require every referenced PDF under data/reports/",
    )
    args = parser.parse_args()
    summary = validate(args.dataset, args.check_reports)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
