.PHONY: install format lint test build run-local run-docker clean

# Local development variables
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
BLACK = $(VENV)/bin/black
ISORT = $(VENV)/bin/isort
FLAKE8 = $(VENV)/bin/flake8

# Docker variables
DOCKER_IMAGE = govwifi-metrics-data-publisher

# Create a virtual environment and install dependencies
install:
	python3 -m venv $(VENV)
	$(PIP) install -U pip setuptools
	$(PIP) install -e .[dev]

# Format code
format:
	$(BLACK) metpub tests
	$(ISORT) metpub tests

# Run linters
lint:
	$(FLAKE8) metpub tests
	$(BLACK) --check metpub tests
	$(ISORT) --check-only metpub tests

# Run tests
test:
	$(PYTEST) tests/

# Run application locally
run-local:
	$(PYTHON) -m metpub.cli

# Build docker image
build:
	docker build --target production -t $(DOCKER_IMAGE):latest .

# Run tests in docker
docker-test:
	docker build --target test -t $(DOCKER_IMAGE):test .

# Clean up
clean:
	rm -rf $(VENV) .pytest_cache *.egg-info build dist __pycache__ metpub/__pycache__ tests/__pycache__
