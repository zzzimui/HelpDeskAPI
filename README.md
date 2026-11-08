# Help Desk API

![HelpDesk screenshot](helpdesk_hero.jpg)

API REST para gerenciamento de chamados de suporte técnico, desenvolvida com Python e FastAPI. O projeto busca aplicar boas práticas de desenvolvimento backend, organização por módulos, persistência relacional e testes automatizados.

## Tecnologias

- **Python 3.12+**
- **FastAPI** — construção da API REST
- **SQLAlchemy 2.0** — ORM com suporte assíncrono
- **PostgreSQL** — banco de dados relacional
- **Alembic** — gerenciamento de migrations
- **Pydantic** — validação e estruturação de dados
- **JWT** — autenticação baseada em tokens
- **pwdlib** — hashing de senhas
- **pytest** — testes automatizados
- **pytest-cov** — análise de cobertura de testes
- **uv** — gerenciamento de dependências
- **Docker** — suporte ao ambiente de desenvolvimento e testes
- **GitHub Actions** — execução automatizada de testes em CI

## Funcionalidades

### Autenticação e usuários
- Login com autenticação baseada em JWT.
- Geração de access tokens.
- Renovação de tokens por meio de refresh tokens.
- Logout e gerenciamento de refresh tokens.
- Hashing seguro de senhas.
- Gerenciamento de usuários e permissões.

### Gerenciamento de chamados
- Criação e atualização de chamados.
- Consulta e listagem de chamados.
- Controle de status com validação de transições permitidas.
- Atribuição de chamados a agentes de suporte.
- Categorização de chamados.
- Controle de acesso aos chamados conforme usuário e função.

### Categorias e mensagens
- Criação e gerenciamento de categorias.
- Envio e consulta de mensagens associadas aos chamados.

### Histórico e auditoria
- Registro de eventos relacionados aos chamados.
- Armazenamento de alterações para acompanhamento do histórico.


## Arquitetura

O projeto utiliza uma organização modular, separando responsabilidades entre rotas, serviços, modelos, schemas e operações de persistência.

- **Routers:** definem os endpoints HTTP.
- **Services:** concentram as regras de negócio.
- **CRUD:** encapsula operações de acesso e manipulação dos dados.
- **Models:** representam as entidades persistidas no banco.
- **Schemas:** definem os formatos de entrada e saída e a validação dos dados.
- **Migrations:** controlam a evolução do esquema do banco de dados.

## Requisitos

- Python 3.12 ou superior.
- [uv](https://docs.astral.sh/uv/).
- PostgreSQL acessível pela aplicação.
- Docker, caso seja utilizado para executar o banco de dados ou os testes de integração.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/zzzimui/HelpDeskAPI
cd HelpDeskAPI
```

Instale as dependências usando o arquivo de lock:

```bash
uv sync --locked
```

Configure a variável de ambiente `DATABASE_URL` com a URL de conexão do PostgreSQL, conforme a configuração utilizada pela aplicação.

Exemplo:

```env
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/helpdesk
```

> Substitua os valores de exemplo pelas credenciais e pelo banco configurados no seu ambiente. Não versione senhas ou chaves secretas no repositório.

## Banco de dados

Após configurar a conexão, aplique as migrations:

```bash
uv run alembic upgrade head
```

## Executando a aplicação

Inicie o servidor de desenvolvimento:

```bash
uv run uvicorn app.main:app --reload
```

A documentação interativa da API fica disponível, por padrão, em:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Executando com Docker

É necessário ter o Docker instalado e em execução. Na raiz do projeto, crie ou
confirme a existência de um arquivo `.env` com as variáveis exigidas pela
aplicação:

```env
DATABASE_URL=postgresql://helpdesk_user:helpdesk_password@db:5432/helpdesk
PROJECT_NAME=Help Desk API
PROJECT_DESCRIPTION=API para gerenciamento de chamados
SECRET_KEY=gere-uma-chave-secreta-para-o-seu-ambiente
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=defina-uma-senha-segura
```

O `compose.yaml` substitui `DATABASE_URL` dentro dos containers para conectar
ao serviço do banco. Use chaves e senhas próprias, especialmente fora do
ambiente local, e não versione o arquivo `.env`.

Inicie os serviços a partir da raiz do projeto:

```bash
docker compose up --build -d
```

O Compose inicia o PostgreSQL, aguarda o banco ficar disponível e aplica as
migrations antes de iniciar a API. Acompanhe a inicialização com:

```bash
docker compose logs -f
```

Quando os serviços estiverem prontos, acesse a documentação interativa em
`http://127.0.0.1:8000/docs` ou `http://127.0.0.1:8000/redoc`. Para parar os
containers sem remover os dados do banco:

```bash
docker compose down
```

Os dados do PostgreSQL ficam no volume `postgres_data` e são mantidos ao parar
os serviços. Para removê-los também, use `docker compose down -v`.

## Testes

Execute a suíte de testes:

```bash
uv run pytest tests/ -v
```

Para executar os testes com relatório de cobertura:

```bash
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

A suíte atual contém testes unitários, testes de integração e testes relacionados à persistência e às regras de negócio.

## Integração contínua

O projeto possui um workflow de GitHub Actions para executar os testes automaticamente em eventos de `push` e `pull_request`, utilizando um serviço PostgreSQL temporário.

## Objetivo do projeto

Este projeto foi desenvolvido como parte do meu portfólio de estudos em desenvolvimento backend com Python, com foco em construção de APIs REST, modelagem relacional, regras de negócio, autenticação, testes automatizados e organização de código.

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE).