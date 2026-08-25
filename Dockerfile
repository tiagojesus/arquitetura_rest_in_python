FROM python:3.12-slim

# Instala o uv a partir da imagem oficial
COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /uvx /bin/

WORKDIR /code

# Copia só os manifests primeiro para aproveitar cache de camadas
COPY pyproject.toml uv.lock* ./

# Instala dependências (incluindo dev) sem instalar o projeto em si
RUN uv sync --no-install-project

# Código da aplicação
COPY app ./app
COPY tests ./tests

ENV PATH="/code/.venv/bin:$PATH"

# Força UTF-8 em todo I/O do Python (independente do locale do container)
ENV PYTHONUTF8=1 \
    PYTHONIOENCODING=utf-8

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
