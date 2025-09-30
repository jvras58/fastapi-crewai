<h1 align="center">
  <a href="#">Projeto com FastAPI + CrewAI</a>
</h1>

<p align="center">
   Esté projeto Utiliza o FastAPI para servir Agentes inteligentes utilizando o CrewAI
</p>

<p align="center">
  <a href="#memo-sobre-o-projeto">Sobre o Projeto</a> •
  <a href="#rocket-tecnologias">Tecnologias</a> •
  <a href="#clipboard-requisitos">Requisitos</a> •
  <a href="#building_construction-arquitetura">Arquitetura</a> •
  <a href="#information_source-como-usar">Como Usar</a> •
  <a href="#handshake-como-contribuir">Como Contribuir</a> •
  <a href="#memo-licença">Licença</a>
</p>

---

## :memo: Sobre o Projeto

Este projeto é uma aplicação backend construída com **FastAPI**, projetada para gerenciar usuários, papéis, permissões e transações em um sistema baseado em **Role-Based Access Control (RBAC)**. A API suporta autenticação via JWT, autorização granular, auditoria de ações e integração com um banco de dados usando SQLAlchemy como ORM.

### Funcionalidades Principais
- **Autenticação**: Login de usuários com geração de tokens JWT.
- **Autor authorization**: Controle de acesso baseado em papéis e permissões.
- **Gerenciamento de Usuários**: Criação, atualização, listagem e exclusão de usuários.
- **Gestão de Papéis e Permissões**: Atribuição de papéis a usuários e permissões a papéis.
- **Auditoria**: Registro de informações de auditoria (usuário, IP, data de criação/atualização).
- **Testes Automatizados**: Suporte a testes com pytest e cobertura de código.

O projeto é estruturado para ser modular, escalável e seguir boas práticas de desenvolvimento, como separação de responsabilidades e uso de ferramentas modernas de desenvolvimento Python.

---

## :rocket: Tecnologias

Este projeto utiliza as seguintes tecnologias e ferramentas:

- **Linguagem**: [Python 3.12](https://www.python.org/)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Framework web para construção de APIs.
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) - Mapeamento objeto-relacional.
- **Banco de Dados**: [SQLite](https://sqlite.org/) - Banco de dados leve e embarcado.
- **Gerenciador de Dependências**: [Uv Astral](https://docs.astral.sh/uv/) - Gerenciamento de dependências e ambientes virtuais.
- **Migrações**: [Alembic](https://alembic.sqlalchemy.org/) - Gerenciamento de migrações de banco de dados.
- **Testes**: [pytest](https://pytest.org/) com [pytest-cov](https://pytest-cov.readthedocs.io/) para cobertura de testes.
- **Linting e Formatação**: [Ruff](https://github.com/charliermarsh/ruff), [Blue](https://blue.readthedocs.io/), e [isort](https://pycqa.github.io/isort/) para manter o código limpo.
- **Autenticação**: [python-jose](https://github.com/mpdavis/python-jose) para JWT e [bcrypt](https://pypi.org/project/bcrypt/) para hash de senhas.

---

## :clipboard: Requisitos

Para rodar ou contribuir com o projeto, você precisará das seguintes ferramentas instaladas:

| Ferramenta                                         | Versão       | Instalação (Linux/macOS)                     |
|----------------------------------------------------|--------------|----------------------------------------------|
| [Python](https://www.python.org/)                  | 3.12       | `asdf install python 3.12` ou similar      |
| [UV](https://docs.astral.sh/uv/)                   | Latest       | `curl -LsSf https://astral.sh/uv/install.sh | sh |
| [Git](https://git-scm.com/)                        | Latest       | `sudo apt install git` (Linux) ou `brew install git` (macOS) |
| [SQLite](https://sqlite.org/)                      | Latest       | Geralmente pré-instalado, ou `sudo apt install sqlite3` |

**Nota**: Recomendamos o uso do `asdf` para gerenciar versões do Python. Consulte o arquivo `.python-version` para a versão exata do Python utilizada.

---

## :building_construction: Arquitetura

A estrutura do projeto é organizada para promover modularidade e facilitar a manutenção. Abaixo está a organização dos arquivos e diretórios:

```bash
FastAPI/
├── app/                        # Código-fonte principal da aplicação
│   ├── api/                    # Definição de rotas, controladores e esquemas
│   │   ├── assignment/         # Endpoints para designações (usuário-papel)
│   │   ├── authentication/     # Endpoints para autenticação (login, JWT)
│   │   ├── authorization/      # Endpoints para autorizações (papel-transação)
│   │   ├── role/               # Endpoints para gerenciamento de papéis
│   │   ├── transaction/        # Endpoints para gerenciamento de transações
│   │   ├── user/               # Endpoints para gerenciamento de usuários
│   ├── database/               # Configuração do banco de dados (SQLAlchemy)
│   ├── models/                 # Modelos ORM para as entidades do sistema
│   ├── utils/                  # Funções utilitárias (segurança, configurações, etc.)
│   ├── startup.py              # Inicialização da aplicação FastAPI
├── migrations/                 # Scripts de migração do banco de dados (Alembic)
├── seeds/                      # Scripts de seeds para a aplicação
├── tests/                      # Testes automatizados (pytest)
├── .secrets/                   # Arquivos sensíveis (ex.: SECURITY_API_SECRET_KEY)
├── .env-semple                 # Modelo para arquivo de configuração .env
├── alembic.ini                 # Configuração do Alembic
├── uv.lock                    # Lockfile do uv com dependências fixas
├── pyproject.toml              # Configuração do projeto e dependências
├── .gitignore                  # Arquivos e pastas ignorados pelo Git
├── .tool-versions              # Versões das ferramentas utilizadas
```

### Modelo de Dados
O projeto utiliza um modelo de dados baseado em RBAC, com as seguintes entidades principais:
- **User**: Representa os usuários do sistema.
- **Role**: Papéis que definem permissões.
- **Assignment**: Associa usuários a papéis.
- **Transaction**: Operações do sistema (ex.: criar, listar, excluir).
- **Authorization**: Associa papéis a transações, definindo permissões.

---

## :information_source: Como Usar

Siga os passos abaixo para configurar e executar o projeto localmente.

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/fastapi-crewai
cd fastapi-crewai
```

## 2.1 Montando o ambiente

Este repositório esta organizando em um devcontainer.
E para instacia-lo no VSCODE é recomendado as seguintes configurações:

#### Extenções recomendadas

- Name: Remote Development
- Id: ms-vscode-remote.vscode-remote-extensionpack
- Description: An extension pack that lets you open any folder in a container, on a remote machine, or in WSL and take advantage of VS Code's full feature set.
- Version: 0.25.0
- Publisher: Microsoft
- VSCode Marketplace Link: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack

#### Docker Engine

É obrigatório ter o Docker Engine já instalado e cunfigurado. Para mais informações de como instalar o Docker Engine em seu SO, ver em:

- Instruções para instalação do Docker Engine: [Ver o link](https://docs.docker.com/engine/install/)

#### Procedimento para instanciar o projeto no VSCODE
1. Com o pack de extenções instalado,
1. Realize o clone/fork deste repositório,
1. Abra o diretorio deste repositorio no VSCODE como um projeto,
1. Use o Comando _Dev Containers: Reopen in Container_ da paleta de comandos do VSCODE. _(F1, Ctrl+Shift+P)_.

Depois da compilação do container o VSCode abrirá o repositório em um ambiente encapsulado e executando diretamente de dentro do container como configurado nas definições do **/.devconainer**.

---

### 2.2 Configurar o Ambiente
Crie o arquivo `.env` baseado no modelo fornecido:
```bash
cp .env-semple .env
```

Edite o arquivo `.env` com as configurações adequadas. Exemplo:
```plaintext
DB_URL="sqlite:///database.db"
SECURITY_ALGORITHM="HS256"
SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Crie o diretório `.secrets` e adicione o arquivo `SECURITY_API_SECRET_KEY` com um valor seguro:
```bash
mkdir .secrets
echo "SUA_CHAVE_SECRETA_AQUI" > .secrets/SECURITY_API_SECRET_KEY
```

### 3. Instalar Dependências
Ative o ambiente virtual e instale as dependências com o UV:
```bash
uv sync
uv install
```

### 4. Aplicar Migrações
Execute as migrações para criar as tabelas no banco de dados:
A) aplique as migrations existentes:
```bash
alembic upgrade head
```
b) Suba os seedings de RBAC e de usuario admin
```bash
task setup_db
```

### 5. Executar a API
Inicie o servidor FastAPI com o comando:
```bash
task run
```

A API estará disponível em:
- **URL Local**: [http://localhost:8000](http://localhost:8000)
- **Documentação Interativa**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs) (Swagger UI)
- **Documentação Alternativa**: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc) (ReDoc)

### 6. Executar Testes
Para rodar os testes automatizados e verificar a cobertura:
```bash
task test
```

O relatório de cobertura será gerado em `htmlcov/index.html`.

---

## :memo: Licença

Este projeto está licenciado sob a [MIT License](LICENSE). Veja o arquivo `LICENSE` para mais detalhes.

---

## :speech_balloon: Contato

Se tiver dúvidas ou sugestões, entre em contato:
- **Autores**: jvras <jvras58@gmail.com>
