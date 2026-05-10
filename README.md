# CRUD API

API RESTful para gerenciamento de usuários, construída com **FastAPI** e **Python**.

## Funcionalidades

- **Create** — Criar um novo usuário
- **Read** — Listar todos os usuários ou buscar um usuário por ID
- **Update** — Atualizar os dados de um usuário (parcial)
- **Delete** — Remover um usuário
- **Health Check** — Verificar o status da API

### Modelo de Usuário

| Campo | Tipo | Restrições |
|---|---|---|
| `id` | UUID | Chave primária, gerada automaticamente |
| `name` | String (100) | Obrigatório |
| `email` | String (255) | Obrigatório, único |
| `hashed_password` | String (255) | Obrigatório |
| `is_active` | Boolean | Padrão: `true` |
| `created_at` | DateTime (timezone) | Preenchido automaticamente |

### Validação de Senha

- Mínimo de 6 caracteres, máximo de 128
- Pelo menos uma letra minúscula
- Pelo menos uma letra maiúscula
- Pelo menos um dígito

## Endpoints

| Método | Caminho | Descrição |
|---|---|---|
| `POST` | `/users/` | Criar um novo usuário |
| `GET` | `/users/` | Listar todos os usuários |
| `GET` | `/users/{user_id}` | Buscar um usuário por ID |
| `PATCH` | `/users/{user_id}` | Atualizar um usuário |
| `DELETE` | `/users/{user_id}` | Deletar um usuário |
| `GET` | `/health` | Health check |

## Arquitetura

O projeto segue **Clean Architecture** com separação clara de responsabilidades:

- **Routers** (`app/api/routers/`) — Camada HTTP, tratamento de requisições e respostas
- **CRUD** (`app/crud/`) — Lógica de negócio e acesso a dados
- **Models** (`app/models/`) — Entidades ORM
- **Schemas** (`app/schemas/`) — Validação com Pydantic
- **Core** (`app/core/`) — Configuração e banco de dados

## Pré-requisitos

- Python 3.12+
- Poetry

## Executando localmente

### 1. Instalar as dependências

```bash
poetry install
```

### 2. Configurar variáveis de ambiente (opcional)

Crie um arquivo `.env` na raiz do projeto:

```env
APP_NAME=CRUD API
DATABASE_URL=sqlite+aiosqlite:///./app.db
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> Os valores padrão já funcionam sem o `.env`.

### 3. Iniciar o servidor

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Acessar a API

- **API:** `http://localhost:8000`
- **Documentação interativa (Swagger):** `http://localhost:8000/docs`
- **Documentação ReDoc:** `http://localhost:8000/redoc`
- **Health check:** `GET http://localhost:8000/health`

## Exemplos de uso

### Criar um usuário

```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"name":"João Silva","email":"joao@example.com","password":"Pass1word"}'
```

### Listar todos os usuários

```bash
curl http://localhost:8000/users/
```

### Buscar um usuário por ID

```bash
curl http://localhost:8000/users/<uuid>
```

### Atualizar um usuário

```bash
curl -X PATCH http://localhost:8000/users/<uuid> \
  -H "Content-Type: application/json" \
  -d '{"name":"Maria Silva"}'
```

### Deletar um usuário

```bash
curl -X DELETE http://localhost:8000/users/<uuid>
```

## Tecnologias

- [FastAPI](https://fastapi.tiangolo.com/) — Framework web
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM assíncrona
- [Pydantic](https://docs.pydantic.dev/) — Validação de dados
- [SQLite](https://www.sqlite.org/) — Banco de dados
- [Poetry](https://python-poetry.org/) — Gerenciamento de dependências
- [Ruff](https://docs.astral.sh/ruff/) — Linter
- [MyPy](https://mypy.readthedocs.io/) — Verificação de tipos
