# Spec 03 — Correções do Code Review de 2026-08-25

## Objetivo

Corrigir os problemas encontrados no code review registrado em
`code_review/2026-08-25-revisao-geral.md` (3 críticos, 4 médios, 4 menores),
restaurando a integridade dos arquivos afetados e o cumprimento real da
spec 02 em produção. **Nenhuma funcionalidade nova é criada nesta spec** —
apenas correções e alinhamentos.

## Regras de negócio

- RN01 — O seed do admin DEVE executar no startup real da aplicação (não
  apenas em testes) e permanecer idempotente.
- RN02 — Credenciais iniciais do admin vêm de variáveis de ambiente:
  `ADMIN_EMAIL` (default dev: `admin@local.dev`) e
  `ADMIN_INITIAL_PASSWORD` (default dev: `Admin0.`). Nenhuma credencial
  permanece hard-coded no código.
- RN03 — Exceções de domínio voltam a herdar de `DomainError`; cada classe
  é definida exatamente uma vez.
- RN04 — A conversão de exceções de domínio em HTTP acontece em um único
  lugar: os handlers globais de `app/main.py`. `app/api/deps.py` deixa de
  converter exceções.
- RN05 — Hash de senha usa a biblioteca `bcrypt` diretamente; `passlib`
  é removida das dependências (declarada mas nunca importada).
- RN06 — A spec 02 é atualizada para refletir RN02 (credenciais via env e
  email válido) e o padrão Docker-first na tarefa de validação.

## Contrato da API

Sem alterações de contrato. O comportamento externo da API deve permanecer
idêntico (mesmos endpoints, status codes e payloads).

## Modelo de dados

Sem alterações de esquema.

## Tarefas

- [ ] **T01 — Corrigir `app/db.py`** (resolve C1)
  Remover o bloco duplicado (segunda definição de `engine`,
  `async_session_factory`, `get_session` e `init_db`). Manter uma única
  `init_db` que executa `create_all` **e** `seed_admin_user`.

- [ ] **T02 — Reescrever `app/services/exceptions.py`** (resolve C2)
  Uma definição por classe, todas herdando de `DomainError`:
  `NotFoundError`, `ConflictError`, `AuthenticationError`,
  `InactiveUserError`. Cada uma com mensagem default e construtor que
  aceita mensagem customizada.

- [ ] **T03 — Credenciais do admin via Settings** (resolve C3)
  Adicionar `admin_email` e `admin_initial_password` em
  `app/core/config.py`; atualizar `app/core/seed.py` para usar as settings;
  atualizar `.env.example` com as novas variáveis; ajustar os testes que
  usam `admin`/`Admin0.` fixos para lerem das settings.

- [ ] **T04 — Remover duplicações restantes** (resolve M1, M2)
  `app/core/config.py`: remover o segundo bloco
  `secret_key`/`algorithm`/`access_token_expire_minutes`.
  `app/models/__init__.py`: manter um único `__all__ = ["Item", "User"]`.

- [ ] **T05 — Unificar conversão de exceções** (resolve M3)
  Remover o try/except de `app/api/deps.py` que converte
  `AuthenticationError`/`InactiveUserError` em `HTTPException`; deixar as
  exceções propagarem para os handlers globais do `main.py`.

- [ ] **T06 — Resolver passlib × bcrypt** (resolve M4)
  Remover `passlib[bcrypt]` e adicionar `bcrypt` explícito via
  `docker compose run --rm tools remove passlib` e
  `docker compose run --rm tools add bcrypt`.

- [ ] **T07 — Zerar o ruff** (resolve m1, m2)
  Corrigir F401 (imports não usados), UP017 (`datetime.timezone.utc` →
  `datetime.UTC`), I001 (ordenação). Configurar no `pyproject.toml`
  ignores justificados: `B008` (idiomático do FastAPI) e `EXE002`
  (bit executável herdado do Windows/OneDrive). Mover imports do corpo
  das funções de teste para o topo dos arquivos.

- [ ] **T08 — Robustecer `tests/test_docs.py`** (resolve m3)
  O teste do caminho desabilitado deve reutilizar `create_app()` com
  `settings.docs_enabled` monkeypatchado, em vez de construir uma app
  paralela manual.

- [ ] **T09 — Atualizar a spec 02** (resolve m4 + alinhamento RN02/RN06)
  Registrar nela as mudanças de credenciais via env e substituir
  `uv run pytest` por `docker compose run --rm tests` na tarefa T04.

- [ ] **T10 — Validação final (Docker)**
  1. `docker compose run --rm tests` → 100% passando;
  2. `docker compose run --rm tools run ruff check .` → 0 erros;
  3. `docker compose down -v && docker compose up -d --build` →
     `SELECT email FROM "user"` no Postgres contém o admin (prova de que
     o seed roda no startup real) + login do admin retorna 200.

## Critérios de aceite

- [ ] Nenhum arquivo contém blocos duplicados (db.py, config.py,
  exceptions.py, models/__init__.py).
- [ ] Seed executa no startup real: banco recriado do zero contém o admin.
- [ ] Nenhuma credencial hard-coded no código-fonte.
- [ ] `docker compose run --rm tests` passa com todos os testes
  (existentes + ajustados).
- [ ] `ruff check .` retorna 0 erros.
- [ ] Contrato externo da API inalterado.
