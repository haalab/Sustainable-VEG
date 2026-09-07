.PHONY: validate test

validate:
	python scripts/validate_dataset.py
	python -m compileall -q scripts

test:
	python -m unittest discover -s tests -v
