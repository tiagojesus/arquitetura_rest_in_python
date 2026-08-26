# Code Review 2026-08-25 — Revisão Geral do Projeto

**Data:** 2026-08-25
**Escopo:** todo o projeto (specs 00, 01, 02)
**Revisor:** arquiteto (IA)
**Status:** concluído — correções propostas na spec `03-correcoes-code-review.spec`

---

## 1. Resumo executivo

A base arquitetural está sólida: camadas respeitadas, specs bem escritas,
cobertura de testes boa (24 testes), fluxo Docker-first funcionando.
**Porém, a implementação das specs 01/02 contém defeitos graves de
qualidade** — arquivos com blocos duplicados (sintoma de edição mal
resolvida pela IA codificadora) e um **bug funcional real: o seed de admin
não executa no startup em produção** (confirmado: tabela `user` vazia no
Postgres em execução). Os testes passam por acidente — o `conftest.py`
chama o seed diretamente, mascarando o bug.

**Veredito: 3 problemas críticos, 4 médios, 4 menores. Não recomendar
novas features até corrigir os críticos.**

---

## 2. Problemas críticos 🔴

### C1 — `app/db.py`: módulo inteiro duplicado; seed nunca roda no startup

O arquivo contém **duas definições completas** de `engine`,
`async_session_factory`, `get_session` e `init_db` (linhas 12–35 e 37–57).
A segunda `init_db` sobrescreve a primeira — e **não chama
`seed_admin_user`**.

- **Impacto:** spec 02 quebrada em produção. Verificado:
  `SELECT email FROM "user"` no container retorna **vazio** — o admin não
  existe. Critério de aceite da spec 02 ("ao subir com banco vazio, admin
  existe") está marcado `[x]` mas é **falso** fora dos testes.
- **Correção:** remover o bloco duplicado, mantendo uma única `init_db`
  com o seed.

### C2 — `app/services/exceptions.py`: arquivo corrompido

`AuthenticationError` e `InactiveUserError` definidos **duas vezes**;
`NotFoundError` tem restos do corpo de outra classe dentro dela
(linhas 46–50). Adicionalmente, as exceções **perderam a herança de
`DomainError`** do design original — o handler genérico de `DomainError`
no `main.py` virou código morto para essas exceções.

- **Correção:** reescrever o arquivo com uma definição por classe,
  restaurando a hierarquia (`AuthenticationError(DomainError)` etc.).

### C3 — Credenciais do admin hard-coded (`app/core/seed.py`)

`email="admin"`, senha `"Admin0."` fixos no código — viola a regra 4 do
AGENTS.md (nunca hard-codar credenciais) e a spec 02 (que define email
`admin`, que **não é um email válido** — o campo aceita qualquer string).
A senha do admin deveria vir de variável de ambiente (ex.:
`ADMIN_INITIAL_PASSWORD`) com fallback apenas para dev.

- **Correção:** mover credenciais para `Settings`; alinhar a spec 02
  (email válido ou justificativa).

---

## 3. Problemas médios 🟡

| # | Problema | Local |
|---|---|---|
| M1 | Bloco `secret_key`/`algorithm`/`access_token_expire_minutes` **duplicado** (linhas 18–20 e 24–26) — PIE794 | `app/core/config.py` |
| M2 | `__all__` definido 2×; a segunda versão omite `User` | `app/models/__init__.py` |
| M3 | **Dupla conversão de exceções**: `deps.py` converte `AuthenticationError`/`InactiveUserError` em `HTTPException`, mas o `main.py` já tem handlers globais. Dois mecanismos para o mesmo problema — viola S (SOLID) | `app/api/deps.py` vs `app/main.py` |
| M4 | `pyproject.toml` declara `passlib[bcrypt]`, mas `security.py` usa `bcrypt` diretamente (funciona por transitividade). Escolher um dos dois | `pyproject.toml` / `app/core/security.py` |

## 4. Problemas menores 🟢

| # | Problema |
|---|---|
| m1 | **59 erros de ruff**: 33× EXE002 (arquivos `.py` com bit executável sem shebang — permissões), 11× B008 (`Depends()` em default argument — idiomático do FastAPI, configurar ignore), 4× F811 (duplicações acima), 3× F401 (imports não usados), 2× UP017 (`timezone.utc` → `UTC`), 1× I001 |
| m2 | Imports dentro do corpo de funções de teste (`tests/test_auth.py` linhas 38–40, 117–121) — mover para o topo |
| m3 | `tests/test_docs.py` testa o caminho desabilitado construindo uma app paralela manual em vez de reutilizar `create_app()` — teste frágil, não testa o código real |
| m4 | Spec 02 marca validação com `uv run pytest` — fora do padrão Docker-first (deveria ser `docker compose run --rm tests`) |

## 5. Pontos positivos ✅

- Camadas respeitadas em todo o código novo (routes finas, negócio nos
  services, queries nos repositories) — aderência à seção 4 do AGENTS.md
- Segurança bem aplicada: resposta 401 genérica (anti user-enumeration),
  `hashed_password` nunca exposto, força de senha validada, email
  normalizado case-insensitive, `last_login_at` rastreado
- Specs 01/02 bem escritas, com RNs claras e critérios de aceite
  mensuráveis
- Cobertura de testes acima do exigido (caminho feliz + múltiplos erros
  por endpoint)
- `swagger_ui_init_oauth`, `docs_enabled`, handlers globais de exceção —
  boas decisões

## 6. Evidências objetivas coletadas

| Verificação | Resultado |
|---|---|
| `docker compose run --rm tests` | 24 passed (mascarado pelo seed no conftest) |
| `ruff check .` | 59 erros (ver m1) |
| `SELECT email FROM "user"` no Postgres em execução | **vazio** — seed não rodou (C1) |

## 7. Plano de correção

Convertido na spec `specs/03-correcoes-code-review.spec` (tarefas T01–T09).
