# ==========================================
# Builder Stage
# ==========================================
FROM --platform=linux/amd64 python:3.11-slim as builder

WORKDIR /app

# Install system dependencies if required for building packages
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY . .
# Install the package and dependencies to a local directory so we can copy them
RUN pip install --user --no-cache-dir .

# ==========================================
# Test Stage
# ==========================================
FROM --platform=linux/amd64 builder as test

COPY . /app
# Install test dependencies
RUN pip install --user --no-cache-dir .[dev]

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Run linting and tests
CMD ["sh", "-c", "flake8 metpub tests && black --check metpub tests && isort --check-only metpub tests && pytest tests/"]

# ==========================================
# Production Stage
# ==========================================
FROM --platform=linux/amd64 python:3.11-slim as production

# Create a non-root user
RUN useradd -m -s /bin/bash appuser

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY --chown=appuser:appuser metpub/ /app/metpub/
COPY --chown=appuser:appuser pyproject.toml /app/

# Switch to the non-root user
USER appuser

# The application runs via the CLI
CMD ["metpub"]
