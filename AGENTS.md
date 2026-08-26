# AGENTS.md — Regras e Estrutura do Projeto

Este documento é o **contrato entre o arquiteto (humano) e a IA codificadora**.
Toda IA que trabalhar neste repositório DEVE ler este arquivo antes de escrever
qualquer código e DEVE seguir todas as regras abaixo sem exceção.

---

## 1. Stack tecnológica (imutável)

| Camada | Tecnologia | Observação |
|---|---|---|
| Linguagem | Python 3.12+ | gerenciado pelo `uv` |
| Gerenciador de pacotes | **uv** | nunca usar `pip`/`poetry`/`conda` |
| Framework web | **FastAPI** | ASGI, servido por `uvicorn` |
| Modelagem/validação | **Pydantic v2** | schemas de entrada/saída |
| ORM | **SQLModel** | tabelas do banco (Pydantic + SQLAlchemy) |
| Banco de dados | **PostgreSQL 16** | driver `psycopg` (v3, binary) |
| Containers | **Docker + Docker Compose** | único ambiente de execução suportado |

> ❌ **Proibido** introduzir novas dependências sem justificativa em spec aprovada.

---

## 2. Fluxo de trabalho orientado a specs

A IA **nunca escreve código sem uma spec**. O fluxo obrigatório é:

1. **Ler a spec** em `specs/NN-nome-da-funcionalidade.spec`.
2. **Executar as tarefas** listadas na spec, na ordem, marcando cada uma como
   concluída (`[x]`) no próprio arquivo ao finalizar.
3. **Validar**: rodar `docker compose up --build` e executar os testes
   (`docker compose run --rm tests`) antes de declarar a spec concluída.
4. **Não implementar nada fora da spec.** Se surgir necessidade nova, criar uma
   nova spec (próximo número sequencial) e reportar ao arquiteto.

### Formato obrigatório de uma spec

Arquivo: `specs/NN-nome-da-funcionalidade.spec` (NN = número sequencial com 2
dígitos, nome em kebab-case). Conteúdo em Markdown:

```markdown
# Spec NN — Nome da Funcionalidade

## Objetivo
Descrição clara do que a funcionalidade faz e por quê.

## Regras de negócio
- RN01 — ...
- RN02 — ...

## Contrato da API (se aplicável)
- `POST /recurso` — descrição, request, response, códigos de erro

## Modelo de dados
Campos, tipos, constraints e relacionamentos.

## Tarefas
- [ ] T01 — Criar modelo SQLModel em `app/models/...`
- [ ] T02 — Criar schemas Pydantic em `app/schemas/...`
- [ ] T03 — Criar repositório em `app/repositories/...`
- [ ] T04 — Criar service em `app/services/...`
- [ ] T05 — Criar rotas em `app/api/routes/...`
- [ ] T06 — Escrever testes em `tests/...`
- [ ] T07 — Validar com `docker compose up --build` e `docker compose run --rm tests`

## Critérios de aceite
- [ ] ...
```

---

## 3. Estrutura do projeto

```
.
├── AGENTS.md                  # este arquivo — regras da IA
├── specs/                     # especificações de funcionalidades
│   └── 00-crud-de-exemplo.spec
├── code_review/               # histórico de code reviews (ver regra abaixo)
├── app/
│   ├── __init__.py
│   ├── main.py                # factory da aplicação FastAPI
│   ├── core/
│   │   └── config.py          # Settings (pydantic-settings), env vars
│   ├── db.py                  # engine, sessão e dependência get_session
│   ├── models/                # tabelas SQLModel (1 arquivo por entidade)
│   ├── schemas/               # DTOs Pydantic (Create/Update/Read)
│   ├── repositories/          # acesso ao banco (queries, CRUD)
│   ├── services/              # regras de negócio (orquestra repositórios)
│   └── api/
│       └── routes/            # routers FastAPI (1 arquivo por recurso)
├── tests/                     # pytest, espelha a estrutura de app/
├── Dockerfile
├── docker-compose.yml         # serviços: api + db (postgres)
├── pyproject.toml             # dependências gerenciadas pelo uv
├── .env.example               # variáveis de ambiente (copiar para .env)
└── README.md
```

### Histórico de code reviews

A pasta `code_review/` guarda o **histórico de todos os code reviews**
realizados no projeto, para acompanhamento do progresso. Regras:

- Todo code review realizado (pela IA ou por humano) DEVE ser registrado
  nesta pasta como arquivo Markdown.
- Nome do arquivo: `AAAA-MM-DD-titulo-curto.md`
  (ex.: `2026-08-25-revisao-geral.md`).
- O relatório deve conter: data, escopo, resumo executivo, problemas
  classificados por severidade (crítico/médio/menor), evidências objetivas
  e o plano de correção (geralmente uma spec em `specs/`).
- Code review NUNCA implementa correções diretamente: os problemas
  encontrados viram tarefas em uma spec própria, que segue o fluxo normal
  (seção 2) após aprovação do usuário.

---

## 4. Arquitetura em camadas (obrigatória)

O código segue **arquitetura em camadas com fluxo unidirecional**:

```
routes (HTTP) → services (negócio) → repositories (persistência) → models (SQLModel)
                     ↑
              schemas (Pydantic DTOs)
```

### Regras de dependência entre camadas

| Camada | Pode importar | NÃO pode importar |
|---|---|---|
| `api/routes` | schemas, services | repositories, models (direto para lógica) |
| `services` | repositories, schemas, models | FastAPI (Request/Response/HTTPException*) |
| `repositories` | models, db | services, routes, FastAPI |
| `models` | sqlmodel apenas | qualquer camada acima |

\* Exceção aceita: services podem levantar exceções de domínio próprias
(definidas em `app/services/exceptions.py`), que as rotas convertem em
`HTTPException`.

### Regras por camada

- **Routes**: finas. Apenas validam entrada (via schema), chamam o service e
  montam a resposta. Zero regra de negócio. Usar `APIRouter` com
  `prefix` e `tags`. Injetar a sessão via `Depends(get_session)`.
- **Services**: toda regra de negócio vive aqui. Funções puras sempre que
  possível; recebem a sessão como parâmetro.
- **Repositories**: um repositório por agregado/entidade. Métodos com nomes
  explícitos: `get_by_id`, `list`, `create`, `update`, `delete`. Nunca
  retornam schemas — retornam models; a conversão é feita no service/route
  via `response_model`.
- **Models**: apenas definição de tabela (`table=True`). Sem lógica de
  negócio, no máximo defaults e constraints.
- **Schemas**: sufixo obrigatório — `XxxCreate`, `XxxUpdate`, `XxxRead`.
  Nunca expor campos internos (ex.: senha hash, flags de controle) no `Read`.

---

## 5. Convenções de código

- **Codificação UTF-8 obrigatória**: TODOS os arquivos gerados ou editados
  (código, specs, documentação, configs, fixtures) devem ser salvos em
  **UTF-8 sem BOM**. Proibido salvar em CP1252/Windows-1252/Latin-1, mesmo
  no Windows. Leituras e escritas de arquivos em código Python devem sempre
  passar `encoding="utf-8"` explicitamente.
- **Type hints obrigatórios** em todas as assinaturas de função/método.
- **Docstrings** em português, estilo Google, em services e repositories.
  https://google.github.io/styleguide/pyguide.html
- **Nomes**: arquivos e módulos em `snake_case`; classes em `PascalCase`;
  rotas em kebab-case no path (`/itens-de-pedido`).
- **Async**: usar `async def` em rotas, services e repositories sempre que
  houver I/O.
- **Configuração**: nenhum valor hard-coded. Tudo via `Settings`
  (`app/core/config.py`) lendo variáveis de ambiente. Nunca commitar `.env`.
- **Erros**: respostas de erro sempre no formato
  `{"detail": "mensagem clara"}` com status code semanticamente correto
  (400 validação de negócio, 404 não encontrado, 409 conflito, 422 payload
  inválido).
- **IDs**: usar `uuid.UUID` como chave primária, nunca inteiro sequencial.
- **Paginação**: endpoints de listagem aceitam `skip`/`limit` (default
  `0`/`50`, `limit` máximo 100).

## 6. Princípios SOLID (obrigatórios)

Todo código produzido pela IA DEVE respeitar os 5 princípios SOLID, aplicados
à arquitetura em camadas deste projeto:

- **S — Single Responsibility Principle**: cada módulo, classe ou função tem
  uma única responsabilidade (uma única razão para mudar). Routes só tratam
  HTTP, services só regra de negócio, repositories só persistência, models
  só definição de tabela. Se o nome de uma função precisa de "e"
  (`cria_e_notifica`), ela deve ser quebrada em duas.
- **O — Open-Closed Principle**: código aberto para extensão, fechado para
  modificação. Novo comportamento entra como nova classe/função/estratégia —
  nunca como um `if`/`elif` a mais dentro de um service existente. Ex.: um
  novo canal de notificação implementa a interface comum em vez de alterar o
  service de envio.
- **L — Liskov Substitution Principle**: implementações devem ser
  substituíveis sem quebrar o contrato. Um repositório alternativo (ex.:
  fake para testes) deve respeitar exatamente a mesma interface do real —
  mesmas assinaturas, tipos de retorno e exceções de domínio.
- **I — Interface Segregation Principle**: interfaces enxutas e específicas;
  ninguém deve depender de métodos que não usa. A segregação dos schemas em
  `Create`/`Update`/`Read` é aplicação direta deste princípio — mantê-la.
- **D — Dependency Inversion Principle**: camadas superiores dependem de
  abstrações, não de detalhes. Services recebem a sessão (e repositórios)
  por parâmetro — injetados via `Depends` nas rotas — e nunca instanciam
  engine/conexão diretamente. Configuração sempre via `Settings` injetável,
  nunca lida de `os.environ` no meio do código.

## 7. Testes

- Framework: `pytest` (+ `httpx` para testes de API).
- Toda spec só é considerada concluída com testes cobrindo o **caminho feliz**
  e pelo menos **um caso de erro** por endpoint.
- Testes de integração sobem com o Postgres de teste via docker-compose
  (serviço `db` na porta de testes ou banco `*_test`).

## 8. Comandos padrão (Docker-first)

> **Regra de ouro: toda tarefa do projeto roda dentro de containers.**
> Não é necessário (nem recomendado) ter Python/uv instalados na máquina
> hospedeira — apenas Docker e Docker Compose. O `uv` só é usado
> **dentro** dos containers.

> ⛔ **Docker indisponível = tarefa bloqueada.** Antes de qualquer tarefa,
> a IA DEVE verificar que o Docker está funcionando (`docker info` ou
> `docker compose version`). Se o Docker não estiver acessível (daemon
> parado, comando não encontrado, erro de build), a IA DEVE:
> 1. **Parar imediatamente** — não executar a tarefa de nenhuma outra forma
>    (proibido usar Python/uv/pip local, sqlite ou qualquer workaround como
>    substituto);
> 2. **Avisar o usuário** explicitamente de que não está conseguindo
>    utilizar o Docker, descrevendo o erro encontrado;
> 3. **Aguardar** o usuário resolver o problema do Docker antes de
>    continuar.

```bash
# subir o ambiente completo (api + postgres, com hot-reload)
docker compose up --build

# subir em background
docker compose up -d --build

# rodar a suíte de testes
docker compose run --rm tests

# lint e formatação
docker compose run --rm tools run ruff check .
docker compose run --rm tools run ruff format .

# adicionar uma dependência (atualiza pyproject.toml e uv.lock)
docker compose run --rm tools add <pacote>

# executar qualquer comando uv/python dentro do ambiente
docker compose run --rm tools run <comando>

# derrubar o ambiente
docker compose down            # mantém os dados do Postgres
docker compose down -v         # apaga também o volume do banco
```

## 9. O que a IA NUNCA deve fazer

1. Criar código fora do escopo de uma spec existente.
2. Mudar a stack (ex.: trocar SQLModel por SQLAlchemy puro) sem nova spec.
3. Colocar regra de negócio em routes ou repositories.
4. Hard-codar credenciais, URLs ou segredos.
5. Ignorar falhas de teste ou desabilitar testes para "passar".
6. Criar arquivos de documentação adicionais sem pedido explícito.
7. Executar tarefas sem o Docker ou contornar a indisponibilidade dele com
   alternativas locais — se o Docker não estiver funcionando, parar e avisar
   o usuário (ver seção 8).
8. Executar `git push` sem permissão explícita do usuário. Commits locais
   são permitidos quando fizerem parte da tarefa, mas o push para o remoto
   só acontece após o usuário autorizar de forma explícita.
