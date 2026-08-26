# Arquitetura REST em Python

API REST em camadas com **FastAPI + SQLModel + PostgreSQL**, empacotada com
**Docker/Docker Compose** e gerenciada com **uv**. O desenvolvimento é
orientado a specs em `.spec/` — leia `AGENTS.md` antes de codificar.

## Subindo o ambiente

Pré-requisito: apenas **Docker + Docker Compose**. Todo o resto (Python, uv,
dependências, testes, lint) roda dentro dos containers.

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000 (com hot-reload da pasta `app/`)
- Docs interativas (Swagger): http://localhost:8000/docs

## Comandos do dia a dia

```bash
docker compose run --rm tests                 # rodar testes
docker compose run --rm tools run ruff check .   # lint
docker compose run --rm tools add <pacote>    # adicionar dependência
docker compose down                           # derrubar (mantém dados)
```

## Estrutura

Ver `AGENTS.md` (seção 3) — arquitetura em camadas:
`routes → services → repositories → models`, com schemas Pydantic como DTOs.

## Novas funcionalidades

1. Crie `.spec/NN-nome-da-funcionalidade.spec` seguindo o formato de
   `.spec/00-crud-de-exemplo.spec`.
2. Entregue a spec à IA codificadora junto com `AGENTS.md`.
