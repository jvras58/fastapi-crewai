## Nós Iniciais (Pontos de Entrada)

### 1. **Endpoint Raiz**
- **Localização**: `apps.startup:read_root`
- **Função**: Verificação básica de saúde da API
- **Resposta**: `{'message': 'Welcome to API!'}`

### 2. **Endpoints de Autenticação**
- **Router**: `apps.api.authentication.router`
- **Função**: Ponto de entrada para obtenção de tokens JWT
- **Prefixo**: `/auth`

### 3. **Endpoints de Recursos Principais**
- **Usuários**: `apps.api.user.router` - `/users`
- **Roles**: `apps.api.role.router` - `/role`
- **Transações**: `apps.api.transaction.router` - `/transaction`
- **Assignments**: `apps.api.assignment.router` - `/assignment`
- **Autorizações**: `apps.api.authorization.router` - `/authorization`
- **Processamento de Texto IA**: `apps.api.text_processing.router` - `/text-processing`

## Nós de Decisão (Pontos de Ramificação)

### 1. **Middleware de Autorização**
- **Componente**: `AuthorizationMiddleware`
- **Função**: Intercepta todas as requisições e adiciona headers de tempo de processamento
- **Decisão**: Continua o fluxo para o próximo middleware/endpoint

### 2. **Validação de Acesso a Transações**
- **Função**: `validate_transaction_access`
- **Decisão**: Autoriza ou nega acesso baseado no sistema RBAC
- **Exceções**: 
  - `IllegalAccessException` - Acesso negado
  - `AmbiguousAuthorizationException` - Autorização ambígua

### 3. **Autenticação de Usuário**
- **Função**: `get_current_user`
- **Decisão**: Valida token JWT e retorna usuário atual ou falha na autenticação

## Nós Finais (Pontos de Saída)

### 1. **Respostas de Sucesso**
- **Schemas**: 
  - `SimpleMessageSchema` - Mensagens simples
  - Schemas específicos por entidade (User, Role, Transaction, etc.)

### 2. **Respostas de Erro**
- **HTTP 400**: `IntegrityValidationException`
- **HTTP 401**: `IllegalAccessException`, `AmbiguousAuthorizationException`
- **HTTP 404**: `ObjectNotFoundException`
- **HTTP 409**: `ObjectConflitException`

### 3. **Persistência de Dados**
- **Banco de Dados**: SQLite via database.db
- **Sessão**: `get_session`

## Agrupamentos Naturais

### 1. **Sistema de Autenticação e Autorização (RBAC)**
```
User ↔ Assignment ↔ Role ↔ Authorization ↔ Transaction
```
- **User**: `apps.models.user.User`
- **Assignment**: `apps.models.assignment.Assignment`
- **Role**: `apps.models.role.Role`
- **Authorization**: `apps.models.authorization.Authorization`
- **Transaction**: `apps.models.transaction.Transaction`

### 2. **Sistema de Processamento de IA**
- **Controlador**: `TextProcessingController`
- **Modelo**: `ProcessedText`
- **Integração**: CrewAI + LangChain para processamento de texto

### 3. **Camada de Auditoria**
- **Base**: `AbstractBaseModel`
- **Campos**: `audit_user_ip`, `audit_user_login`, `audit_created_at`, `audit_updated_on`

### 4. **Sistema de Migrações**
- **Configuração**: alembic.ini
- **Migrações**: 
  - `00292430c7bd_bigbang.py` - Estrutura inicial
  - `6d421afaf99a_create_processed_data_table.py` - Tabela de dados processados

### 5. **Sistema de Seeds**
- **Dados Iniciais**: `seed_transactions.py`, `seed_super_user.py`
- **Códigos de Operação**: `EnumOperationCode`

### 6. **Camada de Testes**
- **Configuração**: `tests.conftest`
- **Factories**: Padrão Factory para criação de dados de teste
- **Cobertura**: Configurada via pytest-cov
