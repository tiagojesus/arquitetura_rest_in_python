# Spec 02 — Seed de Usuário Administrador

## Objetivo

Garantir que um usuário administrador padrão exista no banco sempre que a
aplicação subir e o esquema for criado/recriado. Útil para demos e testes
manuais sem depender de fluxo de registro.

## Regras de negócio

- **RN01 — Idempotência:** o seed só cria o usuário se ele ainda não existir
  (verificação por email).
- **RN02 — Dados do usuário:**
  - email: `admin`
  - full_name: `Administrador`
  - password: `Admin0.`
  - is_active: `True`
- **RN03 — Senha segura:** a senha deve ser armazenada como hash bcrypt via
  `app.core.security.get_password_hash`, nunca em texto plano.

## Modelo de dados

Usa a tabela `user` criada na Spec 01.

## Tarefas

- [x] **T01 — Módulo de seed**
  Criar `app/core/seed.py` com função assíncrona `seed_admin_user(session)`
  que verifica se existe usuário com email `"admin"` e, se não, cria-o.

- [x] **T02 — Integração no startup**
  Chamar `seed_admin_user` dentro de `app/db.py::init_db` (ou no `lifespan`)
  após `create_all`, garantindo que roda sempre que as tabelas são criadas.

- [x] **T03 — Teste**
  Adicionar teste em `tests/test_auth.py` (ou `tests/test_seed.py`) que:
  - sobe a aplicação;
  - verifica que `POST /auth/login` com `admin` / `Admin0.` retorna 200;
  - verifica que o seed é idempotente (subir 2× não quebra).

- [x] **T04 — Validação**
  Executar `uv run pytest tests/ -v` e garantir que todos os testes passam.

## Critérios de aceite

- [x] Ao subir a aplicação com banco vazio, o usuário `admin` existe e consegue
  logar com senha `Admin0.`.
- [x] O seed não falha nem duplica o usuário se executado múltiplas vezes.
- [x] Todos os testes existentes continuam passando.
