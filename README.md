# GovWifi Metrics Data Publisher

A Python package to convert JSON data into a Tableau `.hyper` extract and publish it to Tableau Cloud.

## Requirements
- Python 3.11+
- Docker (optional, for containerized execution)

## Local Development

1. Create a `.env` file by copying the sample:
   ```bash
   cp .env.sample .env
   ```
2. Update the `.env` file with your actual `TOKEN_VALUE` and any other specific configurations.
3. Install dependencies using the Makefile:
   ```bash
   make install
   ```

### Makefile Targets

- `make install`: Sets up a virtual environment (`.venv`) and installs the project and dev dependencies.
- `make format`: Formats code using `black` and `isort`.
- `make lint`: Runs `flake8`, `black --check`, and `isort --check-only` to ensure code quality.
- `make test`: Runs unit tests via `pytest`.
- `make run-local`: Executes the CLI locally using the virtual environment (reads from `.env`).

## Docker Usage

The project utilizes a multi-stage Docker build.

- **Run Tests in Docker:**
  ```bash
  make docker-test
  ```
- **Build Production Image:**
  ```bash
  make build
  ```
