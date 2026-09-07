# OCR preprocessing

The OCR pipelines render only the benchmark pages referenced in `data/Sustainable-VEG.json` and convert detected regions back to PDF-point coordinates.

- `ocr_chandra/main.py` writes `artifacts/ocr/chandra/<report>/<page>/output.json`.
- `ocr_olm/ocr.py` writes `artifacts/ocr/olm/<report>/<page>/output.json`.

Install `requirements-ocr.txt` and review the model-specific hardware requirements before running either pipeline. OCR outputs are generated artifacts and are intentionally ignored by Git.
