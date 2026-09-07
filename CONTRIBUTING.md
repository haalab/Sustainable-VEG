# Contributing

Corrections to annotations, documentation, and benchmark implementations are welcome. Because the released dataset uses a NoDerivatives license, annotation corrections should normally begin as an issue rather than a modified dataset pull request.

1. Open an issue describing the proposed change and the affected benchmark IDs.
2. Keep source reports, OCR caches, model weights, API responses, and generated results out of Git.
3. Run `make validate` and `make test` before submitting a pull request.
4. For annotation corrections, open an issue containing the report filename, one-based page number, SASB metric code, proposed PDF-point coordinates, and a short rationale. Do not submit or publish a modified `data/Sustainable-VEG.json` without separate permission from the maintainers.

Do not include API keys, confidential material, or third-party documents whose redistribution terms are unclear.

Unless explicitly stated otherwise, code and repository-material contributions intentionally submitted for inclusion are accepted under the Apache License 2.0, consistent with Section 5 of that license. Dataset annotation changes require maintainer review because the released annotation file is separately licensed under CC BY-NC-ND 4.0.
