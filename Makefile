.PHONY: venv install lint test run clean help

help:
	@echo "AMP Video Automation Toolkit - Available Commands"
	@echo "=================================================="
	@echo "make venv      - Create Python virtual environment"
	@echo "make install   - Install package with dev dependencies"
	@echo "make lint      - Run code linting with ruff"
	@echo "make format    - Format code with black"
	@echo "make test      - Run tests with pytest"
	@echo "make run       - Run sample batch (requires .env setup)"
	@echo "make clean     - Remove build artifacts and cache"
	@echo ""

venv:
	python3 -m venv .venv
	. .venv/bin/activate && python -m pip install --upgrade pip

install:
	. .venv/bin/activate && pip install -e ".[dev]"

lint:
	. .venv/bin/activate && ruff check .

format:
	. .venv/bin/activate && black src/ tests/

test:
	. .venv/bin/activate && pytest -q

test-coverage:
	. .venv/bin/activate && pytest --cov=src/amp_video --cov-report=html

run:
	. .venv/bin/activate && python -m amp_video.cli run data/input/samples.csv --concurrency 3

render:
	. .venv/bin/activate && python -m amp_video.cli render data/input/samples.csv --out output/preview

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/
