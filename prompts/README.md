# Prompt templates

- [`prompt_rag.txt`](prompt_rag.txt) asks an LLM to associate a retrieved OCR region with a candidate SASB metric.
- [`prompt_vlm.txt`](prompt_vlm.txt) asks a VLM to return metric-aware evidence boxes directly from a rendered page.

The GGSR instruction is defined alongside its structured response schema in `scripts/run_grid.py` because the grid labels and response type are generated at runtime.

When reporting results, record any prompt modifications together with the resulting prediction CSV.
