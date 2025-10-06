# Copilot Instructions for FastAPI + CrewAI Project

## Project Overview
This is a FastAPI backend with integrated CrewAI agents, built around a Role-Based Access Control (RBAC) system. The project combines traditional REST APIs with intelligent AI conversation capabilities using RAG (Retrieval Augmented Generation).

## Architecture & Service Boundaries

### Core Services
- **`apps/core/`**: Main RBAC API with authentication, authorization, and user management
- **`apps/ia/`**: AI service with CrewAI agents, conversation management, and RAG capabilities  
- **`apps/packpage/`**: Shared utilities, base models, and generic controllers

### Key Components
- **Startup**: `apps/core/startup.py` defines the FastAPI app, middleware stack, and all routers
- **Models**: All SQLAlchemy models must be imported in `apps/core/models/__init__.py` for relationship resolution
- **Base Model**: `apps/packpage/base_model.py` provides `AbstractBaseModel` with audit fields (user_ip, created_at, updated_on, user_login)

## Development Workflows

### Environment Setup
```bash
# Use UV for dependency management (not pip)
uv sync                    # Install dependencies
uv run task run           # Start development server
uv run task test          # Run tests with coverage
```

### Database Migrations
```bash
# Auto-generate migrations (models must be imported in __init__.py first)
./scripts/migrate.sh "description"
alembic upgrade head      # Apply migrations
```

### Docker Development
- Uses `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` base image
- `start.sh` handles PostgreSQL connection waiting and DB setup
- Dev container configuration available for VS Code

## Project-Specific Conventions

### Controller Pattern
All controllers inherit from `GenericController[T]` providing standard CRUD operations:
```python
class UserController(GenericController):
    def __init__(self) -> None:
        super().__init__(User)  # Pass model to generic controller
```

### Router Structure
Each feature has its own `router.py` with FastAPI routers:
- Tag-based organization (Users, Auth, AI Chat, etc.)
- All routers registered in `startup.py` with prefixes

### Authentication & Authorization
- JWT tokens via `python-jose`
- RBAC system: User → Assignment → Role → Authorization → Transaction
- Custom `AuthorizationMiddleware` for request processing (currently minimal)
- Password hashing via `bcrypt` in controller save/update methods

### AI Integration Patterns
- **CrewAI Agents**: Located in `apps/ia/agents/` with role-goal-backstory pattern
- **RAG Service**: `apps/ia/services/rag_service.py` handles document indexing and semantic search
- **LLM Configuration**: Centralized in `apps/packpage/llm.py` using Groq API
- **Conversation Management**: Persistent chat history in database models

### Testing Patterns
- Factory-based test data generation in `tests/factory/`
- `conftest.py` provides TestClient with database session override
- Use `pytest -s -x --cov=apps -vv` for testing with coverage

### Environment Configuration
- **Required**: `GROQ_API_KEY` for AI functionality
- **Optional**: `GOOGLE_API_KEY` for Google embeddings
- Database URL supports SQLite (default) and PostgreSQL
- Audit fields automatically populated via `client_ip.py` middleware

## Integration Points

### Database Session Management
- `apps/core/database/session.py` provides session dependency injection
- All controllers receive `Session` parameter for database operations

### Cross-Service Communication
- Core RBAC services are stateless and authentication-agnostic at the model level
- AI services integrate with core via shared database models (`apps/ia/models/`)
- No direct service-to-service calls; communication via shared database

### External Dependencies
- **CrewAI**: Agent orchestration and task management
- **LangChain**: RAG implementation with FAISS vector store
- **FastAPI**: Web framework with automatic OpenAPI generation
- **Alembic**: Database schema migrations
- **UV**: Modern Python package manager replacing pip/poetry

## File Creation Guidelines

### Adding New Features
1. Create model in `apps/core/models/` and import in `__init__.py`
2. Generate migration with `./scripts/migrate.sh "description"`
3. Create controller extending `GenericController`
4. Add router with appropriate tags and register in `startup.py`
5. Add factory in `tests/factory/` and corresponding test file

### AI Components
- New agents go in `apps/ia/agents/` following the role-goal-backstory pattern
- Tools for agents should be in `apps/ia/tools/`
- RAG-related services belong in `apps/ia/services/`

Remember: This project uses UV (not pip), requires model imports in `__init__.py`, and follows a strict RBAC permission model that should be respected when adding new endpoints.
