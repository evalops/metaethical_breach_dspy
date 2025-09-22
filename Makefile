PYTHON ?= python

setup:
	@echo "Setting up virtual environment and installing dependencies..."
	$(PYTHON) -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements.txt

run:
	@echo "Running experiment with default settings..."
	$(PYTHON) scripts/run_experiment.py

run-training:
	@echo "Running experiment with two training rounds..."
	TRAIN_ROUNDS=2 $(PYTHON) scripts/run_experiment.py

run-sweep:
	@echo "Running parameter sweep over frames_per_item values..."
	for n in 1 3 5; do \
		FRAMES_PER_ITEM=$$n $(PYTHON) scripts/run_experiment.py; \
	done

fmt:
	@echo "Formatting code with ruff..."
	ruff format metaethical_breach

.PHONY: setup run run-training run-sweep fmt