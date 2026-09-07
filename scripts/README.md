# Scripts

| Script | Purpose | Main output |
|:--|:--|:--|
| `validate_dataset.py` | Validate annotations and summarize the benchmark | stdout |
| `build_index.py` | Build per-industry BM25 indices | `artifacts/sasb_idx/` |
| `build_database.py` | Build per-industry dense FAISS indices | `artifacts/sasb_db/` |
| `run_bm25.py` | OCR + BM25 baseline | `results/bm25/prediction.csv` |
| `run_semantic.py` | Dense matching, optionally reranked | `results/semantic*/prediction.csv` |
| `run_rag.py` | Retrieval-augmented generation baseline | `results/rag/prediction.csv` |
| `run_direct.py` | Direct VLM coordinate prediction | `results/direct/prediction.csv` |
| `run_grid.py` | Grid-Guided Spatial Retrieval | `results/grid/prediction.csv` |
| `score.py` | Class-aware IoU-F1@0.5 evaluation | stdout |

Run scripts from the repository root. Paths are configured in [`../config.yaml`](../config.yaml). See [`../docs/REPRODUCTION.md`](../docs/REPRODUCTION.md) for the full workflow.
