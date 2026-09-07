# Sustainable-VEG data card

## Overview

Sustainable-VEG is an evaluation benchmark for locating evidence that supports standardized sustainability disclosures. The released annotation file contains 223 candidate pages from 15 companies and 7 SASB industries. It includes both positive and negative indicator-page examples.

| Statistic | Value |
|:--|--:|
| Annotated pages | 223 |
| Companies | 15 |
| SASB industries | 7 |
| Pages with evidence | 104 |
| Evidence boxes | 147 |

The full benchmark is used as an evaluation set. No official training split is provided.

## Files

- [`Sustainable-VEG.json`](Sustainable-VEG.json): versioned annotations and document references
- `reports/`: local location for the 15 source sustainability-report PDFs; PDF files are gitignored
- [`../metrics/`](../metrics/): SASB-aligned indicator descriptions used by the baselines

Download the report package from the [project's Google Drive folder](https://drive.google.com/drive/folders/1uf5v9DCFWm5wEiVOgcaqFbxmdVwmAXjc?usp=sharing), then place the report PDFs directly under `data/reports/`.

## Record schema

Each JSON object has the following fields:

| Field | Type | Description |
|:--|:--|:--|
| `id` | string | Zero-padded benchmark item ID |
| `page` | integer | One-based PDF page number |
| `label` | string array | Ground-truth evidence boxes; empty for negative pages |
| `company` | string | Normalized company identifier |
| `esg_report` | string | Relative reference to the source report |
| `sasb_report` | string | Relative reference identifying the applicable SASB industry |

Example:

```json
{
  "id": "000",
  "page": 56,
  "label": [
    "98.1149969816208,151.128737926483,826.06499698162,290.388737926483:EM-RM-110a.1"
  ],
  "company": "npc",
  "esg_report": "reports/NPC_全國加油站.pdf",
  "sasb_report": "sasb/SASB-EM-RM.pdf"
}
```

## Bounding-box convention

Labels use this representation:

```text
x1,y1,x2,y2:SASB_METRIC_CODE
```

- Coordinates are PDF points in the original page coordinate space.
- The origin is at the top left; x increases rightward and y increases downward.
- `x1 < x2` and `y1 < y2`.
- Multiple boxes are separated by semicolons in prediction CSV files.
- Multiple ground-truth boxes may be used when evidence is distributed across distinct regions on the same page.

## Industries

| Code | Annotated pages |
|:--|--:|
| EM-RM | 31 |
| FN-CB | 61 |
| HC-BP | 15 |
| HC-MS | 12 |
| IF-GU | 24 |
| TC-HW | 25 |
| TC-SC | 55 |

## Annotation process

Candidate pages were identified from indicator-related sections and company-provided disclosure mappings. Two trained annotators with financial backgrounds independently labeled each indicator-page pair and drew minimal evidence boxes. A third annotator adjudicated disagreements to produce the consolidated annotations.

## Intended use and limitations

Sustainable-VEG is intended to compare fine-grained visual grounding methods and support research on auditable ESG analysis. It is not a complete-report retrieval benchmark, a dataset for ESG scoring, or a substitute for professional sustainability assurance.

The benchmark emphasizes visually complex, non-Latin reports and contains a limited set of companies and industries. Candidate-page evaluation does not measure whether a system can find relevant pages in an entire report. Company size, reporting style, industry, and report length are not independently controlled.

## Validation

Validate the annotations alone:

```bash
python scripts/validate_dataset.py
```

After downloading the reports, also verify document availability:

```bash
python scripts/validate_dataset.py --check-reports
```

## Rights and privacy

The annotation file does not contain personal or confidential data beyond information already published in corporate sustainability reports.

[`Sustainable-VEG.json`](Sustainable-VEG.json) is licensed under [CC BY-NC-ND 4.0](../DATA_LICENSE). You may share the unmodified dataset with attribution for noncommercial purposes; modified versions may not be distributed under this license. Source reports, SASB publications, and SASB-derived content are third-party materials and remain subject to their respective owners' terms. See the complete [`LICENSING.md`](../LICENSING.md) notice.
