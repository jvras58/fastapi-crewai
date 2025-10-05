# Módulo IA - Chat Conversacional com RAG

Este módulo implementa um sistema de chat conversacional usando CrewAI, LangChain e RAG (Retrieval Augmented Generation) integrado ao sistema RBAC do FastAPI.

## 🚀 Funcionalidades

### ✅ Implementado

- **RAG Service**: Sistema de busca semântica com LangChain e FAISS
- **Conversation Agent**: Agente conversacional usando CrewAI
- **API REST**: Endpoints para chat, conversas e documentos
- **Modelos de Dados**: Conversation, Message e Document
- **Integração RBAC**: Conectado ao sistema de autenticação do core
- **Upload de Documentos**: Para alimentar a base de conhecimento

### 🎯 Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/chat/chat` | Enviar mensagem e receber resposta da IA |
| `GET` | `/chat/conversations` | Listar conversas do usuário |
| `POST` | `/chat/conversations` | Criar nova conversa |
| `GET` | `/chat/conversations/{id}` | Obter conversa com mensagens |
| `PUT` | `/chat/conversations/{id}` | Atualizar conversa |
| `POST` | `/chat/documents` | Upload de documento |
| `GET` | `/chat/documents` | Listar documentos |
| `GET` | `/chat/search` | Buscar na base de conhecimento |

## 🛠️ Configuração

### 1. Variáveis de Ambiente

```bash
# Obrigatória para usar a IA
GROQ_API_KEY="your_groq_api_key_here"

# Opcional para Google embeddings  
GOOGLE_API_KEY="your_google_api_key_here"
```

### 2. Dependências

As seguintes dependências foram adicionadas ao `pyproject.toml`:

```toml
"crewai>=0.186.1"
"langchain>=0.3.27"
"langchain-google-genai>=2.1.10"
"faiss-cpu>=1.8.0"
"numpy>=1.24.0"
```

### 3. Migrações do Banco

Execute as migrações para criar as tabelas:

```bash
task automate_migrations "Add IA chat models"
task migrate
```

## 📚 Uso Básico

### 1. Chat Simples

```python
from apps.ia.agents.conversation_agent import ConversationAgent
from apps.ia.services.rag_service import RAGService

rag_service = RAGService()
agent = ConversationAgent(rag_service)
response = agent.process_query("Olá, como você está?")
print(response)
```

### 2. Chat com RAG

```python
from apps.ia.agents.conversation_agent import ConversationAgent
from apps.ia.services.rag_service import RAGService

# Criar serviço RAG e adicionar conhecimento
rag_service = RAGService()
rag_service.add_document_from_text(
    "FastAPI é um framework web moderno...",
    {"source": "docs"}
)

# Criar agente com RAG
agent = ConversationAgent(rag_service)
response = agent.chat("O que é FastAPI?")
```

### 3. Uso da API REST

```bash
# Enviar mensagem de chat
curl -X POST "http://localhost:8000/chat/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, preciso de ajuda",
    "context": "Cliente interessado em produtos"
  }'

# Upload de documento para base de conhecimento
curl -X POST "http://localhost:8000/chat/documents" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Manual do Produto",
    "content": "Este é o conteúdo do manual...",
    "content_type": "text/plain"
  }'
```

## 🏗️ Arquitetura

```
apps/ia/
├── agents/             # Agentes CrewAI
│   ├── conversation_agent.py
│   └── __init__.py
├── api/               # Endpoints REST
│   └── chat/
│       ├── controller.py
│       ├── router.py
│       ├── schemas.py
│       └── __init__.py
├── models/            # Modelos SQLAlchemy
│   ├── conversation.py
│   ├── message.py
│   ├── document.py
│   └── __init__.py
├── services/          # Serviços de negócio
│   ├── rag_service.py
│   └── __init__.py
├── tools/             # Ferramentas para agentes
│   ├── rag_search_tool.py
│   └── __init__.py
└── main.py           # Ponto de entrada
```

## 📊 Modelos de Dados

### Conversation
- Armazena conversas entre usuários e IA
- Relacionado ao User via `user_id`
- Contém título, descrição, timestamps

### Message
- Mensagens individuais (user/assistant/system)
- Relacionada à Conversation
- Conteúdo, role e metadados

### Document  
- Documentos da base de conhecimento
- Conteúdo processado pelo RAG
- Hash para evitar duplicatas

## 🧪 Testes

Execute os testes do módulo IA:

```bash
# Testes específicos do IA
pytest tests/test_ia_chat.py -v

# Todos os testes
task test
```

## 🚀 Exemplos

Veja exemplos de uso em:
- `examples/chat_usage_examples.py` - Exemplos práticos
- `tests/test_ia_chat.py` - Testes e casos de uso

Execute os exemplos:

```bash
cd /workspace
python examples/chat_usage_examples.py
```

## 🔧 Troubleshooting

### Problema: "GROQ_API_KEY not found"
- Configure a chave da API no arquivo `.env`
- Obtenha uma chave gratuita em https://console.groq.com

### Problema: Embeddings não funcionam
- O sistema usa fallback para embeddings simples se Google API não estiver disponível
- Para produção, configure `GOOGLE_API_KEY` ou use outro provider

### Problema: Erros de migração
```bash
# Recriar migrações
rm -rf migrations/versions/*
task automate_migrations "Initial IA models"
task migrate
```

## 📈 Próximos Passos

- [ ] Implementar persistência do vector store
- [ ] Adicionar suporte a upload de arquivos (PDF, DOCX)
- [ ] Implementar cache de respostas da IA
- [ ] Adicionar métricas de uso
- [ ] Implementar diferentes tipos de agentes
- [ ] Suporte a conversas em grupo
- [ ] Interface web para chat

## 🤝 Contribuição

Para contribuir com melhorias:

1. Siga os padrões do projeto (GenericController, AbstractBaseModel)
2. Adicione testes para novas funcionalidades
3. Execute `task lint` e `task format` antes de commit
4. Documente as mudanças no README

## 📄 Licença

Este módulo segue a mesma licença do projeto principal.
