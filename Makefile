# ==============================================================================
# GRC Engineering Platform
# Developer Makefile
# ==============================================================================


PYTHON ?= python3

PIP ?= pip


.PHONY: help install install-dev lint format test validate run clean docker-build docker-run


help:

	@echo ""
	@echo "GRC Engineering Platform"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make install       Install production dependencies"
	@echo "  make install-dev   Install development dependencies"
	@echo "  make lint          Run lint checks"
	@echo "  make format        Format source code"
	@echo "  make test          Run tests"
	@echo "  make validate      Validate configuration/frameworks"
	@echo "  make run           Run engine"
	@echo "  make docker-build  Build container"
	@echo "  make docker-run    Run container"
	@echo "  make clean         Remove generated files"
	@echo ""


install:

	$(PIP) install -r requirements.txt


install-dev:

	$(PIP) install -r requirements-dev.txt


lint:

	ruff check .

	mypy engine collectors


format:

	ruff format .


test:

	pytest -v --cov


validate:

	yamllint config

	python -m engine.validator


run:

	$(PYTHON) -m engine


collect:

	$(PYTHON) -m engine.collect


report:

	$(PYTHON) -m engine.reporting


docker-build:

	docker build \
		-t grc-engineering-platform .


docker-run:

	docker run \
		--env-file .env \
		grc-engineering-platform


clean:

	rm -rf \
		.pytest_cache \
		.mypy_cache \
		.ruff_cache \
		coverage.xml \
		htmlcov \
		build \
		dist
