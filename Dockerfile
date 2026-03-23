# Stage 1: Install dependencies
FROM python:3.12-slim AS builder

ARG FINBOT_EXTRAS=""

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Fallback build toolchain for packages that may not have prebuilt wheels.
# Keeping this in the builder stage avoids bloating the runtime image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN set -eux; \
    extra_args=""; \
    if [ -n "${FINBOT_EXTRAS}" ]; then \
        old_ifs="$IFS"; \
        IFS=','; \
        for extra in ${FINBOT_EXTRAS}; do \
            extra_args="${extra_args} --extra ${extra}"; \
        done; \
        IFS="$old_ifs"; \
    fi; \
    # shellcheck disable=SC2086
    uv sync --frozen --no-dev --no-install-project $extra_args

# Keep pip on a patched version to avoid known container CVEs.
RUN uv pip install --python /app/.venv/bin/python pip==26.0

# Stage 2: Runtime image
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DYNACONF_ENV=development \
    PATH="/app/.venv/bin:$PATH"

# Patch system pip in the runtime image to address Trivy-reported CVEs.
RUN python -m pip install --no-cache-dir --upgrade pip==26.0

# Apply system security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 finbot && \
    useradd --uid 1000 --gid finbot --create-home finbot

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv .venv

# Copy source code
COPY finbot/ finbot/
COPY scripts/ scripts/
COPY DISCLAIMER.md Makefile pyproject.toml ./

# Create data directory (will be mounted as volume)
RUN mkdir -p finbot/data && chown -R finbot:finbot /app

USER finbot

# Default command: show help
ENTRYPOINT ["python", "-m", "finbot.cli.main"]
CMD ["--help"]
