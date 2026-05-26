# GovWifi Metrics Data Publisher

A robust Python CLI tool and package designed to ingest metrics in JSON format, transform the data, generate a high-performance Tableau `.hyper` extract, and publish it directly to Tableau Cloud.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
- [Local Development](#local-development)
  - [1. Setup Virtual Environment](#1-setup-virtual-environment)
  - [2. Configure Environment Variables](#2-configure-environment-variables)
  - [3. Code Formatting & Quality](#3-code-formatting--quality)
  - [4. Running Tests](#4-running-tests)
- [Usage Instructions](#usage-instructions)
  - [Local Execution](#local-execution)
  - [Docker Execution](#docker-execution)
- [Clean Up](#clean-up)

---

## Features

- **JSON Data Parsing**: Efficiently loads structured JSON metrics.
- **Value Mapping / Aliasing**: Automatically maps long metric names to human-readable names compatible with Tableau dashboards.
- **High-Performance Extract**: Converts metrics into Tableau's native high-performance `.hyper` database format using `pantab`.
- **Automated Publishing**: Programmatically authenticates with Tableau Cloud via Personal Access Tokens (PATs) and updates/overwrites target data sources dynamically.

---

## Requirements

- **Python 3.11+**
- **Docker** (optional, for containerized execution and testing)

---

## Configuration

The application uses environment variables for configuration, which can be stored in a `.env` file in the root directory.

### Environment Variables

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **`TOKEN_NAME`** | *Required* | - | Personal Access Token (PAT) name generated in Tableau Cloud. |
| **`TOKEN_VALUE`** | *Required* | - | Secret PAT value associated with `TOKEN_NAME`. |
| **`SITE_ID`** | *Required* | - | The Tableau Cloud Site ID / Content URL. |
| **`SERVER_URL`** | *Required* | - | The base URL of the Tableau Cloud server (e.g., `https://prod-uk-a.online.tableau.com`). |
| **`PROJECT_NAME`** | *Required* | - | Target project folder in Tableau Cloud where the data source resides. |
| **`DATASOURCE_NAME`**| *Required* | - | The name of the published Data Source in Tableau Cloud. |
| **`JSON_FILE_PATH`** | *Optional* | `<year>_govwifi_data.json` | Path to the source JSON metrics file. Dynamically defaults to using the current/resolved year. |
| **`HYPER_FILE_PATH`**| *Optional* | `<year>_govwifi_data.hyper`| Destination path for the generated `.hyper` extract. Dynamically defaults to using the current calendar year. |
| **`TABLE_NAME`** | *Optional* | `Extract` | The table name inside the Hyper extract. **Must be set to `Extract` for standard single-table extracts (see important note below).** |
| **`METRICS_API_URL`**| *Required (Recovery)* | - | The base URL of the GovWifi Metrics API. |
| **`METRICS_API_KEY`**| *Required (Recovery)* | - | Bearer token key for the GovWifi Metrics API. |
| **`RECOVER_YEAR`**   | *Optional* | *Current calendar year* | Year to recover metrics data for. |
| **`RECOVER_MONTH`**  | *Optional* | - | Optional month (1-12) to recover metrics data for. |

> [!IMPORTANT]
> **Tableau Single-Table Extract Naming Requirement**: 
> Tableau strictly requires single-table extracts to have their internal table named exactly **`Extract`**. 
> - When you keep the default value (`Extract`), Tableau maps the fields perfectly on every overwrite without regenerating the logical metadata, ensuring your dashboard's auto-generated fields and calculations remain stable.
> - **Do not change** the `TABLE_NAME` variable unless you are working with a highly specialized multi-table schema.

---

## Local Development

Follow these steps to set up the repository for local development:

### 1. Setup Virtual Environment

Use the provided `Makefile` target to create a virtual environment (`.venv`) and install all required package and development dependencies in editable mode:

```bash
make install
```

### 2. Configure Environment Variables

Create your `.env` file from the provided sample template and update the variables with your credentials:

```bash
cp .env.sample .env
```

### 3. Code Formatting & Quality

Before submitting pull requests or committing code, format and check the codebase using the configured linting suite.

- **Auto-Format Code** (runs `black` and `isort`):
  ```bash
  make format
  ```
- **Lint Code** (runs `flake8`, `black --check`, and `isort --check-only`):
  ```bash
  make lint
  ```

### 4. Running Tests

- **Run local unit tests** (runs `pytest` on the local machine):
  ```bash
  make test
  ```
- **Run tests in Docker** (executes linters and unit tests in a container mimicking the CI environment):
  ```bash
  make docker-test
  ```

---

## Usage Instructions

The publisher can be executed locally inside the virtual environment or within a Docker container.

### Local Execution

You can run the publishing pipeline locally using several methods:

1. **Via Makefile (Recommended)**:
   This target loads your `.env` configurations automatically and runs the main module:
   ```bash
   make run-local
   ```

2. **Via Package CLI Entrypoint**:
   Once the package is installed via `make install`, you can invoke the global CLI command directly:
   ```bash
   # Make sure the virtual environment is activated
   source .venv/bin/activate
   metpub
   ```

3. **Via Python Module Execution**:
   ```bash
   .venv/bin/python -m metpub.cli
   ```

### Metrics Data Recovery

You can download and save metrics data for a specific year or month using the `recover` CLI command.

#### 1. Ingesting Metrics Data via `recover`
To recover data for the current calendar year (default output is `<current_year>_govwifi_data.json`):
```bash
source .venv/bin/activate
recover
```

To recover data for a specific year and month:
```bash
recover --year 2025 --month 5
```
This streams the recovery JSON data directly from the metrics endpoint. 
- If a month is provided, the output file defaults to `<year>_<month:02d>_govwifi_data.json` (e.g. `2025_05_govwifi_data.json`).
- If no month is provided, the output file defaults to `<year>_govwifi_data.json` (e.g. `2025_govwifi_data.json`).
- You can override this output file location using the `JSON_FILE_PATH` environment variable.

#### 2. Publishing Recovered Data via `metpub`
Once the recovery JSON data is downloaded, you can publish it to Tableau Cloud by passing the downloaded file path to `metpub`:
```bash
# This reads from the downloaded file and publishes it
JSON_FILE_PATH=2025_05_govwifi_data.json HYPER_FILE_PATH=2025_05_govwifi_data.hyper metpub
```

### Docker Execution

For automated, serverless, or containerized environments, you can build and run the production image.

1. **Build the Production Image**:
   ```bash
   make build
   ```

2. **Run the Container**:
   Pass your `.env` configuration file to the docker run command. If your JSON input file is located on the host, mount it into the `/app` working directory:
   ```bash
   docker run --rm \
     --env-file .env \
     -v $(pwd)/2026_govwifi_data.json:/app/2026_govwifi_data.json \
     govwifi-metrics-data-publisher:latest
   ```

---

## Clean Up

To clean the workspace by removing the virtual environment, pytest cache, Python bytecode (`__pycache__`), and temporary package build artifacts:

```bash
make clean
```
