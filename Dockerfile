# Tutorial runtime image: Python + uv + project dependencies.
# Kept intentionally simple — a single stage, no multi-stage build, because
# this is for local learning, not production deployment.

FROM python:3.11-slim

# Copy the uv binary from its official image (fastest, no curl|sh).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Some ZenML transitive deps (e.g. psutil) fall back to building from source
# on linux/arm64. Install the toolchain + Python headers so `uv sync` works
# regardless of wheel availability. Cleaned up in the same layer to keep size down.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential python3-dev \
    && rm -rf /var/lib/apt/lists/*

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

# Install deps first for better layer caching — only rebuilds when pyproject changes.
COPY pyproject.toml ./
RUN uv sync --no-install-project

# Project files come in via a bind mount at runtime (see docker-compose.yml),
# so edits on the host are reflected live inside the container.

CMD ["sleep", "infinity"]
