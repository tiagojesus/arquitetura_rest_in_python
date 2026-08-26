# Spec 02 — Seed de Usuário Administrador

> **Atualizada pela Spec 03 (code review 2026-08-25):** credenciais do admin
> passaram a vir de variáveis de ambiente (RN02) e a validação segue o
> padrão Docker-first (T04).

## Objetivo

Garantir que um usuário administrador padrão exista no banco sempre que a
aplicação subir e o esquema for criado/recriado. Útil para demos e testes
manuais sem depender de fluxo de registro.

## Regras de negócio

- **RN01 — Idempotência:** o seed só cria o usuário se ele ainda não existir
  (verificação por email).
- **RN02 — Dados do usuário (via variáveis de ambiente):**
  - email: valor de `ADMIN_EMAIL` (default dev: `admin@local.dev`)
  - full_name: `Administrador`
  - password: valor de `ADMIN_INITIAL_PASSWORD` (default dev: `Admin0.`)
  - is_active: `True`
  - Nenhuma credencial fica hard-coded no código-fonte; em produção as
    variáveis são obrigatórias e secretas.
- **RN03 — Senha segura:** a senha deve ser armazenada como hash bcrypt via
  `app.core.security.get_password_hash`, nunca em texto plano.

## Modelo de dados

Usa a tabela `user` criada na Spec 01.

## Tarefas

- [x] **T01 — Módulo de seed**
  Criar `app/core/seed.py` com função assíncrona `seed_admin_user(session)`
  que verifica se existe usuário com o email configurado e, se não, cria-o.

- [x] **T02 — Integração no startup**
  Chamar `seed_admin_user` dentro de `app/db.py::init_db` após `create_all`,
  garantindo que roda sempre que as tabelas são criadas.
  *(Corrigido na Spec 03 — T01: a duplicação de `init_db` fazia o seed nunca
  executar no startup real.)*

- [x] **T03 — Teste**
  Testes em `tests/test_auth.py`:
  - sobe a aplicação;
  - verifica que `POST /auth/login` com as credenciais das settings retorna 200;
  - verifica que o seed é idempotente (subir 2× não quebra).

- [x] **T04 — Validação**
  Executar `docker compose run --rm tests` e garantir que todos os testes
  passam.

## Critérios de aceite

- [x] Ao subir a aplicação com banco vazio, o usuário admin existe e consegue
  logar com a senha de `ADMIN_INITIAL_PASSWORD`.
- [x] O seed não falha nem duplica o usuário se executado múltiplas vezes.
- [x] Todos os testes existentes continuam passando.
