# Chandra preprocessing

From the repository root:

```bash
pip install -r requirements-ocr.txt
python scripts/ocr/ocr_chandra/main.py
```

The script reads the benchmark annotation file and source reports from `data/reports/`, then writes page-level OCR objects with `bbox_pdf` coordinates under `artifacts/ocr/chandra/`.
