---
title: Ecom-Dashboard
emoji: "📊"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Ecom Dashboard

Streamlit + DuckDB e-commerce analytics dashboard. Deployed on Hugging Face Spaces (Docker SDK).

## Architecture

```
ecom.py                composition root
ui/                    Streamlit views (tabs + components)
analytics/             pure functions: aggregations, funnel, brand-eval, KPI, RFM, cohort, CLV, basket, Markov, time-series
charts/                ChartPort protocol + Plotly + Chart.js backends
data/                  DataRepository protocol + DuckDB / in-memory backends, parquet files
infra/                 config (env-first) + mailer (SMTP/Noop)
assets/                CSS + GA snippet
scripts/               one-shot migrations
tests/                 pytest unit + integration
```

Layering rule: `ui` → `analytics | charts | data | infra`. The pure layers do not import from `ui`.

## Local development (Docker)

Single source of truth for dependencies: `pyproject.toml` (PEP 621).
Runtime deps are under `[project.dependencies]`; test/lint deps under `[project.optional-dependencies.dev]`.

Build the dev image (includes pytest + ruff):

```sh
docker build --build-arg INSTALL_DEV=true -t ecom-dashboard:dev .
```

Or build the slim production image:

```sh
docker build -t ecom-dashboard:prod .
```

Run:

```sh
docker run --rm -p 7860:7860 --env-file .env ecom-dashboard:dev
```

Open http://localhost:7860.

### One-shot data migration (pickle → parquet)

```sh
docker run --rm -v "$PWD":/app -w /app ecom-dashboard:dev \
    python scripts/migrate_pickle_to_parquet.py
```

### Tests

```sh
docker run --rm -v "$PWD":/app -w /app ecom-dashboard:dev pytest
```

### Lint

```sh
docker run --rm -v "$PWD":/app -w /app ecom-dashboard:dev ruff check .
```

## Environment variables

See `.env.example`. On Hugging Face Spaces, configure these as Space secrets — they are exposed as env vars.

## Deployment (Hugging Face Spaces)

1. Push to a HF Space repo with `sdk: docker` (set in YAML frontmatter at the top of this README).
2. Set Space secrets to mirror `.env.example`.
3. The Space builds the `Dockerfile` and runs the `CMD` line on port 7860 (HF default).

## License

(unset)
