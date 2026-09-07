# SPDX-License-Identifier: Apache-2.0
"""Evaluate Sustainable-VEG predictions with class-aware IoU-F1@0.5."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IOU_THR = 0.5
BOX_SEP = ";"


def _safe_split_boxes(value: object) -> list[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text or text.upper() == "NONE":
        return []
    return [part.strip() for part in text.split(BOX_SEP) if part.strip()]


def _parse_box_str(box_str: str) -> tuple[float, float, float, float, str]:
    if ":" not in box_str:
        raise ValueError(f"Invalid box '{box_str}': expected x1,y1,x2,y2:code")
    coord, code = box_str.split(":", 1)
    values = [value.strip() for value in coord.split(",")]
    if len(values) != 4:
        raise ValueError(f"Invalid box '{box_str}': expected four coordinates")
    x1, y1, x2, y2 = map(float, values)
    if not (x1 < x2 and y1 < y2):
        raise ValueError(f"Invalid box '{box_str}': require x1 < x2 and y1 < y2")
    if not code.strip():
        raise ValueError(f"Invalid box '{box_str}': metric code is empty")
    return x1, y1, x2, y2, code.strip()


def _iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    intersection = max(0.0, min(ax2, bx2) - max(ax1, bx1)) * max(
        0.0, min(ay2, by2) - max(ay1, by1)
    )
    union = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - intersection
    return intersection / union if union > 0 else 0.0


def _evaluate_image(
    ground_truth: list[tuple[float, float, float, float, str]],
    predictions: list[tuple[float, float, float, float, str]],
    iou_threshold: float = IOU_THR,
) -> tuple[int, int, int]:
    gt_by_code: dict[str, list[tuple[float, float, float, float]]] = {}
    pred_by_code: dict[str, list[tuple[float, float, float, float]]] = {}
    for x1, y1, x2, y2, code in ground_truth:
        gt_by_code.setdefault(code, []).append((x1, y1, x2, y2))
    for x1, y1, x2, y2, code in predictions:
        pred_by_code.setdefault(code, []).append((x1, y1, x2, y2))

    true_positive = false_positive = false_negative = 0
    for code in gt_by_code.keys() | pred_by_code.keys():
        gt_boxes = gt_by_code.get(code, [])
        pred_boxes = pred_by_code.get(code, [])
        candidates = sorted(
            (
                (_iou(gt_box, pred_box), gt_index, pred_index)
                for gt_index, gt_box in enumerate(gt_boxes)
                for pred_index, pred_box in enumerate(pred_boxes)
            ),
            reverse=True,
        )
        matched_gt: set[int] = set()
        matched_pred: set[int] = set()
        for iou, gt_index, pred_index in candidates:
            if iou < iou_threshold:
                break
            if gt_index in matched_gt or pred_index in matched_pred:
                continue
            matched_gt.add(gt_index)
            matched_pred.add(pred_index)

        true_positive += len(matched_gt)
        false_positive += len(pred_boxes) - len(matched_pred)
        false_negative += len(gt_boxes) - len(matched_gt)

    return true_positive, false_positive, false_negative


def _parse_index(rows: Iterable[tuple[str, object]]) -> dict[str, list[tuple[float, float, float, float, str]]]:
    index: dict[str, list[tuple[float, float, float, float, str]]] = {}
    for sample_id, raw_boxes in rows:
        sample_id = str(sample_id).strip()
        if not sample_id:
            raise ValueError("Encountered an empty sample ID")
        if sample_id in index:
            raise ValueError(f"Duplicate sample ID: {sample_id}")
        index[sample_id] = [_parse_box_str(box) for box in _safe_split_boxes(raw_boxes)]
    return index


def load_annotations(path: Path) -> dict[str, list[tuple[float, float, float, float, str]]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return _parse_index((item["id"], ";".join(item.get("label", []))) for item in data)


def load_submission(path: Path) -> dict[str, list[tuple[float, float, float, float, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not {"ID", "TARGET"}.issubset(reader.fieldnames):
            raise ValueError(f"{path} must contain ID and TARGET columns")
        return _parse_index((row["ID"], row.get("TARGET", "")) for row in reader)


def score_indices(
    solution: dict[str, list[tuple[float, float, float, float, str]]],
    submission: dict[str, list[tuple[float, float, float, float, str]]],
    iou_threshold: float = IOU_THR,
) -> tuple[float, float, float]:
    true_positive = false_positive = false_negative = 0
    for sample_id in solution.keys() | submission.keys():
        tp, fp, fn = _evaluate_image(
            solution.get(sample_id, []), submission.get(sample_id, []), iou_threshold
        )
        true_positive += tp
        false_positive += fp
        false_negative += fn

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "submissions",
        nargs="*",
        type=Path,
        help="prediction CSV files; defaults to results/*/prediction.csv",
    )
    parser.add_argument(
        "--annotations",
        type=Path,
        default=PROJECT_ROOT / "data" / "Sustainable-VEG.json",
        help="ground-truth annotation JSON",
    )
    parser.add_argument("--iou", type=float, default=IOU_THR, help="IoU match threshold")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 0.0 <= args.iou <= 1.0:
        raise ValueError("--iou must be between 0 and 1")
    submissions = args.submissions or sorted((PROJECT_ROOT / "results").glob("*/prediction.csv"))
    if not submissions:
        raise FileNotFoundError("No prediction CSV supplied and none found under results/")

    solution = load_annotations(args.annotations)
    for submission_path in submissions:
        prediction = load_submission(submission_path)
        precision, recall, f1 = score_indices(solution, prediction, args.iou)
        print(
            f"{submission_path}: precision={precision:.4f} "
            f"recall={recall:.4f} F1@{args.iou:g}={f1:.4f}"
        )


if __name__ == "__main__":
    main()
