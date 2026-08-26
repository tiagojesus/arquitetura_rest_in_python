# Spec 00 — CRUD de Exemplo (Item)

## Objetivo

Implementar um CRUD completo da entidade `Item` para servir como **referência
viva da arquitetura em camadas**. Todas as próximas specs devem seguir o mesmo
padrão estabelecido aqui. Esta spec também valida que o ambiente
Docker + Postgres + FastAPI sobe de ponta a ponta.

## Regras de negócio

- RN01 — Todo `Item` possui `name` (obrigatório, 1–120 caracteres) e
  `description` (opcional, até 500 caracteres).
- RN02 — `name` deve ser único; conflito retorna HTTP 409.
- RN03 — A exclusão é física (hard delete) neste CRUD de referência.
- RN04 — Listagens são paginadas com `skip`/`limit` (default 0/50, máx 100).

## Contrato da API

| Método | Rota | Descrição | Respostas |
|---|---|---|---|
| GET | `/health` | Health check da API | 200 |
| POST | `/items` | Cria um item | 201, 409, 422 |
| GET | `/items` | Lista itens paginados | 200 |
| GET | `/items/{id}` | Busca por id | 200, 404 |
| PATCH | `/items/{id}` | Atualização parcial | 200, 404, 409 |
| DELETE | `/items/{id}` | Remove o item | 204, 404 |

- Request de criação (`ItemCreate`): `{"name": "str", "description": "str | null"}`
- Request de atualização (`ItemUpdate`): todos os campos opcionais.
- Response (`ItemRead`): `{"id": "uuid", "name": "str", "description": "str | null", "created_at": "datetime"}`

## Modelo de dados

Tabela `item`:

| Campo | Tipo | Constraint |
|---|---|---|
| id | UUID | PK, default `uuid4` |
| name | VARCHAR(120) | NOT NULL, UNIQUE, index |
| description | VARCHAR(500) | NULL |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` |

## Tarefas

- [x] T01 — Criar modelo SQLModel em `app/models/item.py`
- [x] T02 — Criar schemas Pydantic em `app/schemas/item.py`
- [x] T03 — Criar repositório em `app/repositories/item.py`
- [x] T04 — Criar service em `app/services/item.py`
- [x] T05 — Criar rotas em `app/api/routes/items.py` e registrar no `main.py`
- [x] T06 — Escrever testes em `tests/test_items.py`
- [x] T07 — Validar com `docker compose up --build` e `docker compose run --rm tests`

## Critérios de aceite

- [x] `docker compose up --build` sobe `api` + `db` sem erros.
- [x] `GET /health` retorna `{"status": "ok"}`.
- [x] Criar item com nome duplicado retorna 409 com `{"detail": "..."}`.
- [x] Buscar/deletar id inexistente retorna 404.
- [x] `docker compose run --rm tests` passa com testes de caminho feliz + erro por endpoint.
