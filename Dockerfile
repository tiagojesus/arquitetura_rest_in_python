# syntax=docker/dockerfile:1
# Dockerfile multi-stage — ver AGENTS.md (Docker-first).
#
# Estágios:
#   base  → imagem Python + uv + env UTF-8 (compartilhada por todos)
#   deps  → dependências de produção (camada cacheada: só rebuilda se
#           pyproject.toml/uv.lock mudarem)
#   dev   → deps + dependências de dev + código + testes (targets: dev)
#   api   → deps + código, imagem enxuta de produção (target: api)
#
# Builds usam cache mount do uv (BuildKit): pacotes baixados são reaproveitados
# entre builds, reduzindo drasticamente o tempo de rebuild.

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /code

# uv copiado da imagem oficial (pin de versão para builds reproduzíveis)
COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /uvx /bin/

# ---------------------------------------------------------------------------
FROM base AS deps

# Só os manifests: enquanto eles não mudarem, esta camada (e as seguintes)
# saem do cache, mesmo com o código da aplicação alterado.
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ---------------------------------------------------------------------------
FROM deps AS dev

# Dependências de desenvolvimento (pytest, ruff, etc.) por cima das de prod
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY app ./app
COPY tests ./tests

ENV PATH="/code/.venv/bin:$PATH"

# Usado pelos serviços `tests` e `tools` do docker-compose
CMD ["pytest", "-v"]

# ---------------------------------------------------------------------------
FROM deps AS api

COPY app ./app

ENV PATH="/code/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
