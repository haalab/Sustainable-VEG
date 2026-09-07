# SPDX-License-Identifier: Apache-2.0
import csv
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import score  # noqa: E402


class ScoreTests(unittest.TestCase):
    def test_exact_class_aware_match(self):
        solution = {"000": [(0.0, 0.0, 10.0, 10.0, "TC-SC-1")]}
        prediction = {"000": [(0.0, 0.0, 10.0, 10.0, "TC-SC-1")]}
        self.assertEqual(score.score_indices(solution, prediction), (1.0, 1.0, 1.0))

    def test_wrong_metric_is_not_a_match(self):
        solution = {"000": [(0.0, 0.0, 10.0, 10.0, "TC-SC-1")]}
        prediction = {"000": [(0.0, 0.0, 10.0, 10.0, "TC-SC-2")]}
        self.assertEqual(score.score_indices(solution, prediction), (0.0, 0.0, 0.0))

    def test_csv_loader_preserves_leading_zero_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prediction.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["ID", "TARGET"])
                writer.writerow(["000", "NONE"])
            self.assertIn("000", score.load_submission(path))


if __name__ == "__main__":
    unittest.main()
