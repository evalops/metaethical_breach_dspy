.PHONY: help install test clean run experiment

help:
	@echo "Metaethical Breach DSPy - AI Safety Research Framework"
	@echo ""
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  clean       Clean temporary files"
	@echo "  experiment  Run the metaethical pressure test"
	@echo "  help        Show this help message"

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest tests/ -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/

experiment:
	@echo "Running metaethical pressure test..."
	@echo "Make sure to set MODEL and API_BASE environment variables"
	python scripts/run_experiment.py

# Development targets
dev-install: install
	python -m pip install pytest black isort

format:
	black metaethical_breach/ scripts/ tests/
	isort metaethical_breach/ scripts/ tests/

lint:
	black --check metaethical_breach/ scripts/ tests/
	isort --check-only metaethical_breach/ scripts/ tests/
