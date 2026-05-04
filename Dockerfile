# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# uv installs Python deps 10-100x faster than pip and caches across builds.
COPY --from=ghcr.io/astral-sh/uv:0.5.8 /uv /uvx /usr/local/bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# --- Layer 1: dependencies (cache-friendly) ---
# pyproject.toml + README.md is enough for uv to resolve and install all deps.
# Stub package directories let setuptools register the project; real source comes in Layer 2.
COPY pyproject.toml README.md ./
RUN mkdir -p analytics charts data infra ui/tabs ui/components \
    && for d in analytics charts data infra ui ui/tabs ui/components; do \
           touch "$d/__init__.py"; \
       done

ARG INSTALL_DEV=false
# Editable install ensures host-mounted code edits are picked up at runtime
# (volume-mounting /app would otherwise be shadowed by site-packages).
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ "$INSTALL_DEV" = "true" ]; then \
        uv pip install --system -e ".[dev]"; \
    else \
        uv pip install --system -e "."; \
    fi

# --- Layer 2: actual source (overlays the stubs) ---
COPY . .

# Generate parquet rollups from the source pickles. Idempotent. Cached as long
# as the source pickles + the migration script are unchanged.
RUN python scripts/migrate_pickle_to_parquet.py

EXPOSE 7860

CMD ["streamlit", "run", "ecom.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
