# Gestor Imobiliário

## 🚀 Setup Rápido

### Pré-requisitos

- Python 3.11+
- [UV](https://docs.astral.sh/uv/) instalado

### 1. Instalar UV (se necessário)

```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clonar e configurar o projeto

```bash
# Clonar o repositório
git clone https://github.com/Luishma34/GestorImobiliario.git
cd GestorImobiliario

# Criar ambiente virtual e instalar dependências
uv sync
```

### 4. Executar migrations

```bash
# Criar a primeira migration (se ainda não existir)
uv run alembic revision --autogenerate -m "Setup inicial"

# Aplicar migrations
uv run alembic upgrade head
```

### 5. Rodar a aplicação

```bash
uv run uvicorn app.main:app --reload
```

### 6. Acessar documentação

- Swagger UI: http://localhost:8000/docs
- Se estiver usando WSL: http://127.0.0.1:8000/docs

## 🔧 Comandos Úteis

```bash
# Instalar dependências
uv sync

# Adicionar nova dependência
uv add nome-do-pacote

# Criar nova migration
uv run alembic revision --autogenerate -m "descrição da mudança"

# Aplicar todas as migrations pendentes
uv run alembic upgrade head

# Reverter última migration
uv run alembic downgrade -1

# Ver histórico de migrations
uv run alembic history

# Rodar api
uv run uvicorn app.main:app --reload

```

## 🔄 Alternando entre SQLite e PostgreSQL

Basta comentar a variável `DATABASE_URL` no arquivo `.env` do banco atual e descomentar a do banco desejado:

Após alterar, se o banco não estiver atualizado, execute as migrations novamente:

```bash
uv run alembic upgrade head
```

