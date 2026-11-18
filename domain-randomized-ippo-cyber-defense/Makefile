.PHONY: install test train evaluate figures all
install:
	pip install -r requirements.txt && pip install -e .
test:
	pytest -q
train:
	python scripts/train.py --method baseline --seeds 0 1 2
	python scripts/train.py --method dr --seeds 0 1 2
evaluate:
	python scripts/evaluate.py --mode matrix --seed 0
	python scripts/evaluate.py --mode multiseed
figures:
	python scripts/make_figures.py results
all: install test train evaluate figures
