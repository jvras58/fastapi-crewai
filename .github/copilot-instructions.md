# FastAPI + CrewAI Copilot Instructions

## Architecture Overview

This is a **modular FastAPI application** with AI integration capabilities using CrewAI and LangChain. The project has a dual-service architecture:

- **`apps/core/`**: Complete RBAC (Role-Based Access Control) API with FastAPI, SQLAlchemy, JWT auth
- **`apps/ia/`**: AI orchestration service (currently placeholder for CrewAI agents)

Key architectural decisions:
- **Monolithic structure** with modular separation between REST API (`core`) and AI services (`ia`) 
- **Generic controller pattern** for consistent CRUD operations across all entities
- **Comprehensive audit trail** with IP tracking and user attribution on all database operations
- **Factory-based testing** with isolated in-memory SQLite for each test

## Essential Project Patterns

### Database Models & ORM
All models inherit from `AbstractBaseModel` (in `apps/core/utils/base_model.py`) which provides:
```python
audit_user_ip: Mapped[str] 
audit_created_at: Mapped[datetime]
audit_updated_on: Mapped[datetime] 
audit_user_login: Mapped[str]
```

**Column naming convention**: Use `name=` parameter with descriptive prefixes:
- `str_` for strings: `display_name: Mapped[str] = mapped_column(name='str_display_name')`
- `id` for primary keys: `id: Mapped[int] = mapped_column(primary_key=True, name='id')`

### API Structure Pattern
Each API module follows strict organization:
```
apps/core/api/{entity}/
├── controller.py    # Business logic, inherits GenericController
├── router.py       # FastAPI routes with dependency injection
└── schemas.py      # Pydantic models for request/response
```

**Router dependencies pattern**:
```python
DbSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

### Controller Inheritance
Extend `GenericController` for consistent CRUD:
```python
class UserController(GenericController):
    def __init__(self) -> None:
        super().__init__(User)  # Pass model to parent
```

Override `save()`/`update()` for special logic (e.g., password hashing in UserController).

### Authentication & Authorization
- JWT tokens via `python-jose` 
- Route protection using `get_current_user` dependency
- Transaction-based authorization system (users → roles → transactions)
- Client IP tracking via `get_client_ip(request)` utility

## Critical Developer Workflows

### Environment Setup
```bash
uv sync                    # Install dependencies
task setup_db             # Run migrations + seed data  
task run                  # Start development server
```

### Database Operations  
```bash
task automate_migrations "description"  # Auto-generate migration
task migrate                            # Apply pending migrations
task seed_super_user                   # Create admin user
task seed_transactions                 # Seed transaction data
```

### Testing & Quality
```bash
task test                 # Run tests with coverage
task lint                 # Check code style (ruff + blue)  
task format               # Auto-format code (blue + isort)
```

### Docker Development
```bash
docker compose up         # PostgreSQL + FastAPI containers
# App runs on :8000, PostgreSQL on :5433
```

## Key Configuration Files

- **`pyproject.toml`**: Dependencies, dev tools, taskipy commands
- **`apps/core/utils/settings.py`**: Environment configuration with `.env` + `.secrets/` support
- **`alembic.ini`**: Database migration configuration  
- **`compose.yml`**: PostgreSQL + app containers with environment injection

## Testing Conventions

Tests use **factory-boy pattern** with isolated sessions:
- `tests/factory/`: Model factories for consistent test data
- `tests/conftest.py`: SQLite in-memory setup with automatic cleanup
- Each test gets fresh database via `session` fixture
- Client fixture provides TestClient with dependency overrides

## AI Integration Points

The `apps/ia/` module is designed for CrewAI agent orchestration. Current dependencies include:
- `crewai>=0.186.1`
- `langchain>=0.3.27` 
- `langchain-google-genai>=2.1.10`

Environment expects `GROQ_API_KEY` for AI model access.

## Important Notes

- **All model operations require audit fields**: Set `audit_user_ip` and `audit_user_login` on create/update
- **Use taskipy commands** instead of direct tool calls: `task run` not `uvicorn ...`
- **Database URLs**: SQLite for development (`database.db`), PostgreSQL for containers
- **API documentation**: Available at `/api/v1/docs` (Swagger) and `/api/v1/redoc`
