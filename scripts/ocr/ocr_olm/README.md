# olmOCR preprocessing

Run from the repository root after installing `requirements-ocr.txt` and placing source PDFs under `data/reports/`:

```bash
python scripts/ocr/ocr_olm/ocr.py
```

Outputs are written to `artifacts/ocr/olm/<report-stem>/<page>/`. Each `output.json` object includes a `bbox_pdf` field in the coordinate system used by the evaluator.

If a run saved `output_raw.txt` and `meta.json` but strict JSON post-processing did not finish, retry it with:

```bash
python scripts/ocr/ocr_olm/postprocess_from_raw.py
```

`html_table_to_description.py` is an optional experimental normalization step. Write its output to a separate directory so the raw OCR artifacts remain available.
