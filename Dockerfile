# Stage 1: Install dependencies
FROM python:3.13-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install --no-cache-dir poetry==2.3.2

WORKDIR /app

# Copy dependency files first (better layer caching)
COPY pyproject.toml poetry.lock ./

# Install dependencies into a virtual environment
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-ansi --only main

# Stage 2: Runtime image
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DYNACONF_ENV=development \
    PATH="/app/.venv/bin:$PATH"

# Create non-root user
RUN groupadd --gid 1000 finbot && \
    useradd --uid 1000 --gid finbot --create-home finbot

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv .venv

# Copy source code
COPY finbot/ finbot/
COPY scripts/ scripts/
COPY Makefile pyproject.toml ./

# Create data directory (will be mounted as volume)
RUN mkdir -p finbot/data && chown -R finbot:finbot /app

USER finbot

# Default command: show help
ENTRYPOINT ["finbot"]
CMD ["--help"]
