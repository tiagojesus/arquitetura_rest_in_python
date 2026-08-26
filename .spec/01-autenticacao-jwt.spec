# Spec 01 — Autenticação JWT

## Objetivo

Implementar fluxo completo de autenticação baseada em JWT: registro de usuários,
login com OAuth2 Password Flow (Bearer token), logout semântico e proteção de
rotas. A funcionalidade deve respeitar a arquitetura em camadas e servir de
referência para autorização futura.

## Regras de negócio

- **RN01 — Email como identificador único:** o `email` é obrigatório, único na
  base e case-insensitive para login.
- **RN02 — Força de senha:** mínimo de 8 caracteres, contendo pelo menos uma
  letra maiúscula, uma minúscula e um dígito.
- **RN03 — Tempo de vida do token:** o JWT de acesso expira após 30 minutos
  (configurável via variável de ambiente `ACCESS_TOKEN_EXPIRE_MINUTES`).
- **RN04 — Usuário ativo:** apenas usuários com `is_active=True` podem autenticar
  e acessar rotas protegidas.
- **RN05 — Respostas de erro sem vazamento:** credenciais inválidas retornam
  HTTP 401 genérico (`{"detail": "Credenciais inválidas"}`); usuário inativo
  retorna HTTP 403 (`{"detail": "Usuário inativo"}`).
- **RN06 — Segurança da senha:** o campo `hashed_password` nunca é exposto em
  nenhum schema de resposta.
- **RN07 — Logout stateless:** `POST /auth/logout` é uma rota protegida que
  retorna sucesso (200); a invalidação do token ocorre no client-side
  (descarte do Bearer), pois JWT é stateless por design.
- **RN08 — Rastreamento de login:** a cada autenticação bem-sucedida o campo
  `last_login_at` do usuário é atualizado com o timestamp UTC atual.
- **RN09 — Documentação protegida para execução:** a URL `/docs` (Swagger UI)
  pode ser acessada livremente para visualização, mas o "Try it out" / execução
  de qualquer endpoint protegido exige autenticação via JWT Bearer.
- **RN10 — Documentação condicional ao ambiente:** o acesso a `/docs` só deve
  estar habilitado quando a variável de ambiente `DOCS_ENABLED` for `true`.
  Por padrão (quando a variável não está definida) o valor é `true`, ou seja,
  `/docs` fica disponível em desenvolvimento. Em produção deve-se definir
  `DOCS_ENABLED=false`.

## Contrato da API

| Método | Rota            | Descrição                           | Auth   | Respostas     |
|--------|-----------------|-------------------------------------|--------|---------------|
| POST   | `/auth/register`| Registra um novo usuário            | —      | 201, 409, 422 |
| POST   | `/auth/login`   | Autentica e retorna JWT Bearer      | —      | 200, 401, 422 |
| POST   | `/auth/logout`  | Logout semântico (client descarta)  | Bearer | 200, 401      |
| GET    | `/auth/me`      | Retorna dados do usuário logado     | Bearer | 200, 401, 403 |

### Detalhes dos payloads

- **Register request (`UserCreate`)**
  ```json
  {
    "email": "usuario@exemplo.com",
    "full_name": "Nome Completo",
    "password": "Str0ng!"
  }
  ```

- **Login request (`application/x-www-form-urlencoded` ou JSON)**
  Compatível com `OAuth2PasswordRequestForm`:
  - `username` (email)
  - `password`

- **Login response (`Token`)**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

- **Me response (`UserRead`)**
  ```json
  {
    "id": "uuid",
    "email": "usuario@exemplo.com",
    "full_name": "Nome Completo",
    "is_active": true,
    "last_login_at": "2026-08-25T20:00:00Z",
    "created_at": "2026-08-25T20:00:00Z"
  }
  ```

- **Logout response**
  ```json
  {
    "detail": "Logout realizado com sucesso. Descarte o token no client."
  }
  ```

## Modelo de dados

Tabela `user`:

| Campo           | Tipo         | Constraint                          |
|-----------------|--------------|-------------------------------------|
| id              | UUID         | PK, default `uuid4`                 |
| email           | VARCHAR(255) | NOT NULL, UNIQUE, index             |
| full_name       | VARCHAR(120) | NOT NULL                            |
| hashed_password | VARCHAR(255) | NOT NULL                            |
| is_active       | BOOLEAN      | NOT NULL, default `True`            |
| last_login_at   | TIMESTAMPTZ  | NULL                                |
| created_at      | TIMESTAMPTZ  | NOT NULL, default `now()`           |

## Tarefas

- [x] **T01 — Dependências**
  Adicionar `pyjwt`, `python-multipart` e `bcrypt` ao projeto.

- [x] **T02 — Configurações de segurança**
  Atualizar `app/core/config.py` incluindo:
  `secret_key: str`, `algorithm: str = "HS256"`,
  `access_token_expire_minutes: int = 30`, `docs_enabled: bool = True`.

- [x] **T03 — Utilitários de segurança**
  Criar `app/core/security.py` com funções puras:
  `verify_password(plain, hashed) -> bool`,
  `get_password_hash(plain) -> str`,
  `create_access_token(data: dict, expires_delta: timedelta | None) -> str`,
  `decode_access_token(token: str) -> dict`.

- [x] **T04 — Exceções de domínio**
  Criar `app/services/exceptions.py` com:
  `AuthenticationError`, `InactiveUserError`, `ConflictError`,
  `NotFoundError`, `DomainError`.

- [x] **T05 — Modelo SQLModel**
  Criar `app/models/user.py` com a tabela `User` conforme modelo de dados.

- [x] **T06 — Schemas Pydantic**
  Criar `app/schemas/user.py` (`UserCreate`, `UserRead`) e
  `app/schemas/auth.py` (`Token`, `TokenPayload`).

- [x] **T07 — Repositório**
  Criar `app/repositories/user.py` com `UserRepository`:
  `get_by_email`, `get_by_id`, `create`.

- [x] **T08 — Service de autenticação**
  Criar `app/services/auth.py` com `AuthService`:
  `register`, `authenticate`, `get_current_user`.
  O método `authenticate` deve atualizar `last_login_at` no momento do login
  bem-sucedido.

- [x] **T09 — Dependency de proteção**
  Criar `app/api/deps.py` com `get_current_user` que injeta o token do header
  `Authorization`, utiliza `AuthService` e retorna o usuário autenticado.

- [x] **T10 — Rotas**
  Criar `app/api/routes/auth.py` com os quatro endpoints descritos no contrato
  (`register`, `login`, `logout`, `me`) e registrar o router no `app/main.py`
  com prefixo `/auth` e tag `"Autenticação"`.

- [x] **T11 — Testes**
  Criar `tests/test_auth.py` cobrindo:
  - registro com sucesso (201);
  - registro com email duplicado (409);
  - login com sucesso e retorno de JWT (200);
  - login com credenciais inválidas (401);
  - login com usuário inativo (403);
  - acesso a `/auth/me` com token válido (200);
  - acesso a `/auth/me` sem token (401);
  - acesso a `/auth/me` com token expirado (401);
  - logout com token válido retorna 200;
  - `last_login_at` é atualizado após login bem-sucedido.

- [x] **T12 — Validação**
  Executar testes e garantir que os testes da Spec 00 continuam passando.

- [x] **T13 — Flag de ambiente para `/docs`**
  Atualizar `app/core/config.py` adicionando `docs_enabled: bool = True`.

- [x] **T14 — Condicional de disponibilidade do `/docs`**
  Em `app/main.py`, configurar `docs_url` e `redoc_url` no `FastAPI(...)`:
  - se `docs_enabled=True`, usar os valores padrão (`/docs`, `/redoc`);
  - se `docs_enabled=False`, desabilitar ambos (`None`).

- [x] **T15 — Proteção do "Try it out" no Swagger**
  Configurar `swagger_ui_init_oauth` no `FastAPI(...)`,
  de modo que o Swagger UI exija o token Bearer para executar rotas protegidas,
  mas continue permitindo acesso anônimo à visualização da documentação.

- [x] **T16 — Testes de documentação**
  Criar `tests/test_docs.py` cobrindo:
  - `GET /docs` retorna 200 quando `DOCS_ENABLED=true`;
  - `GET /docs` retorna 404 quando `DOCS_ENABLED=false`;
  - a interface do Swagger exibe o botão de autorização (Authorize) com
    esquema `OAuth2PasswordBearer`.

## Critérios de aceite

- [x] `docker compose up --build` sobe `api` + `db` sem erros.
- [x] `POST /auth/register` cria usuário e retorna `UserRead` (201).
- [x] `POST /auth/register` com email duplicado retorna 409 com `{"detail": "..."}`.
- [x] `POST /auth/login` retorna um JWT válido para credenciais corretas (200).
- [x] `POST /auth/login` com senha ou email errado retorna 401.
- [x] `POST /auth/login` atualiza o campo `last_login_at` do usuário no banco.
- [x] `GET /auth/me` com token válido retorna os dados do usuário (200).
- [x] `GET /auth/me` sem token ou com token inválido/expirado retorna 401.
- [x] `GET /auth/me` com usuário inativo retorna 403.
- [x] `POST /auth/logout` com token válido retorna 200.
- [x] Nenhuma response expõe `hashed_password` ou `password`.
- [x] `docker compose run --rm tests` passa com 100% dos cenários da Spec 01.
- [x] `GET /docs` retorna 200 quando `DOCS_ENABLED=true` (padrão).
- [x] `GET /docs` retorna 404 quando `DOCS_ENABLED=false`.
- [x] O Swagger UI exige autenticação Bearer para executar endpoints protegidos,
  mas permite visualização anônima da documentação.
