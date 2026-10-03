## Migrações do banco

As migrações usam PostgreSQL e a URL definida no arquivo `.env` (`DATABASE_URL`).
Execute os comandos a partir da raiz do projeto.

### Primeira migração

Para criar o banco de teste do zero, remova o schema atual e aplique o baseline:

```powershell
uv run alembic upgrade head
```

O baseline atual está em `alembic/versions/2ef7d51b9bf7_create_initial_schema.py` e cria todas as tabelas, enums, chaves estrangeiras e índices definidos pelos modelos SQLAlchemy.

Se o banco de teste já tiver tabelas ou um histórico antigo, recrie o schema antes:

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

Depois execute novamente `uv run alembic upgrade head`.

### Consultar o estado

```powershell
uv run alembic current
uv run alembic heads
uv run alembic history --verbose
uv run alembic check
```

### Criar e aplicar upgrades

Após alterar um modelo:

```powershell
uv run alembic revision --autogenerate -m "descreva a alteracao"
uv run alembic upgrade head
```

Revise o arquivo gerado antes de aplicar, especialmente alterações de colunas `NOT NULL`, enums, chaves estrangeiras e dados existentes.

Para voltar uma revisão:

```powershell
uv run alembic downgrade -1
```

`alembic stamp` altera somente o marcador de versão e não executa alterações no schema. Não use `stamp` para substituir `upgrade`, exceto quando o schema já tiver sido conferido manualmente.


### Execute o código abaixo para criar a seed inicial de categorias
```powershell
uv run alembic upgrade head
```