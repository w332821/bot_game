# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **FastAPI project template** with clean architecture design. It provides a production-ready foundation for building web applications with proper separation of concerns, dependency injection, and middleware support.

## Common Commands

### Setup & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Configure database (copy and edit config file)
cp config.example.yaml config.yaml
# Edit config.yaml with your database credentials

# Initialize database tables
python -m base.init_db
```

### Running the Application
```bash
# Development server (with hot reload)
python biz/application.py
# OR
uvicorn biz.application:app --reload

# Production server (multi-worker)
uvicorn biz.application:app --host 0.0.0.0 --port 8000 --workers 2
```

### Creating New Modules
```bash
# Generate a new business module with complete structure
python scripts/create_module.py <module_name>

# Example: Create a user module
python scripts/create_module.py user
```

## Architecture Overview

### Layer Structure

**Base Layer** (`base/`) - Infrastructure and reusable components:
- `model.py` - Base model with UUID v7, soft delete, automatic timestamps (PST)
- `repo.py` - Generic async repository pattern
- `api.py` - Unified API response wrapper
- `exception.py` - Base exception handling
- `init_db.py` - Database initialization script
- `middleware/` - Built-in middlewares (Request ID, Logging, Exception handling)

**Business Layer** (`biz/`) - Domain-specific modules:
- `application.py` - FastAPI app entry point
- `containers.py` - Dependency injection container
- `[module]/` - Business modules following consistent structure

### Module Organization Pattern

Each business module follows this structure:
```
biz/[module_name]/
├── models/
│   ├── model.py      # SQLModel entities + Create/Update schemas
│   └── schema.py     # API request/response DTOs
├── repo/
│   └── [module]_repo.py    # Data access layer
├── service/
│   └── [module]_service.py # Business logic layer
├── api/
│   └── [module]_api.py     # FastAPI router
└── exception/
    └── exception.py         # Module-specific exceptions
```

## Key Architectural Patterns

### 1. Repository Pattern
All repositories inherit from `BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]`:
- Generic typed with 3 type parameters
- Session-per-operation with async context managers
- Automatic soft delete filtering
- Standard CRUD operations: `get_by_id()`, `list()`, `create()`, `update()`, `delete()`, `remove()`

```python
class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    pass  # Inherits all base functionality
```

### 2. Dependency Injection
Uses `dependency-injector` with centralized container in `biz/containers.py`:
- Configuration from `config.yaml`
- Singleton database engine/session factory
- Factory pattern for repositories and services

**To add a new module:**
1. Register in `containers.py`:
```python
from biz.user.repo.user_repo import UserRepository
from biz.user.service.user_service import UserService

user_repo = providers.Factory(UserRepository, session_factory=db_session_factory)
user_service = providers.Factory(UserService, user_repo=user_repo)
```

2. Register router in `application.py`:
```python
from biz.user.api.user_api import user_api
app.include_router(user_api, prefix=api_prefix)
```

3. Wire module in `application.py`:
```python
container.wire(modules=["biz.user.api.user_api"])
```

### 3. Built-in Middlewares

Three middlewares are enabled by default:

1. **RequestIDMiddleware** - Generates unique request ID for tracking
   - Adds `X-Request-ID` header to responses
   - Stores request_id in `request.state`

2. **LoggingMiddleware** - Logs all requests with timing
   - Logs request start, completion, and errors
   - Adds `X-Process-Time` header

3. **ExceptionMiddleware** - Global exception handling
   - Catches `UnifyException` and returns formatted errors
   - Logs all unhandled exceptions

### 4. Database & ORM
- **SQLModel**: Combines Pydantic + SQLAlchemy ORM
- **Async operations**: All database calls use AsyncSession
- **UUID v7**: Time-sortable primary keys
- **Soft delete**: All models have `deleted` flag
- **Timestamps**: Automatic `create_time`/`modify_time` in Pacific Time

Base model (`base/model.py:ModelBase`):
```python
class ModelBase(SQLModel):
    id: UUID = Field(default_factory=uuid7, primary_key=True)
    create_time: Optional[datetime] = Field(default_factory=date_now)
    modify_time: Optional[datetime] = Field(default_factory=date_now)
    deleted: bool = Field(default=False)
```

All domain models should inherit from `ModelBase`.

### 5. API Response Format
All API responses use `UnifyResponse` wrapper:

Success response:
```json
{
    "code": 200,
    "message": "success",
    "data": { ... }
}
```

Error response:
```json
{
    "code": 100001,
    "message": "error description",
    "data": { ... }
}
```

Always use `response_class=UnifyResponse` on endpoints.

### 6. Exception Handling
Custom exceptions inherit from `UnifyException`:
```python
from enum import IntEnum
from fastapi import status
from base.exception import UnifyException

class UserExceptionCode(IntEnum):
    UserNotFound = 100001

UserNotFound = UnifyException(
    detail="user not found",
    biz_code=UserExceptionCode.UserNotFound,
    http_code=status.HTTP_404_NOT_FOUND
)
```

Raise exceptions in service layer:
```python
if not user:
    raise UserNotFound
```

## Adding New Business Modules

### Option 1: Use Code Generator (Recommended)

```bash
python scripts/create_module.py <module_name>
```

This will:
1. Create complete module structure
2. Generate boilerplate code for models, repo, service, API
3. Show step-by-step instructions for manual registration

### Option 2: Manual Creation

1. Create module directory structure in `biz/[module_name]/`
2. Define SQLModel entities in `models/model.py` (inherit from `ModelBase`)
3. Create repository in `repo/` (inherit from `BaseRepository`)
4. Implement business logic in `service/`
5. Define API router in `api/`
6. Create exceptions in `exception/`
7. Register in `containers.py` and `application.py` (see Dependency Injection section)
8. Run `python -m base.init_db` to create tables

## Development Workflow

### Creating a New Feature
1. Generate module: `python scripts/create_module.py feature_name`
2. Implement models in `models/model.py`
3. Add business logic in `service/`
4. Define API endpoints in `api/`
5. Register dependencies in `containers.py`
6. Register router in `application.py`
7. Wire module in `application.py`
8. Initialize database: `python -m base.init_db`
9. Test endpoints via `/docs`

### Repository Custom Queries
Add custom queries to your repository:
```python
class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, email: str):
        async with self._session_factory() as session:
            result = await session.exec(
                select(self._model).where(
                    self._model.email == email,
                    self._model.deleted == False
                )
            )
            return result.first()
```

### Service Business Logic
Keep business logic in service layer:
```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_create: UserCreate):
        # Check if email exists
        existing = await self.user_repo.get_by_email(user_create.email)
        if existing:
            raise UserAlreadyExists

        # Create user
        return await self.user_repo.create(user_create)
```

## Configuration

Database settings in `config.yaml`:
- `database_uri` - Async connection (mysql+asyncmy://...)
- `sync_database_uri` - Sync connection for initialization (mysql+pymysql://...)
- `echo` - Set to True to log SQL queries (development only)

**IMPORTANT**: Never commit `config.yaml` with real credentials. Use `config.example.yaml` as template.

## URL Structure

Full endpoint URL: `/api/v1/[module]/[endpoint]`
- `/api` - Global prefix
- `/v1/[module]` - Router prefix
- `/[endpoint]` - Endpoint path

Example: `POST /api/v1/user/create`

## Built-in Endpoints

- `/health` - Health check endpoint
- `/docs` - Swagger UI (interactive API documentation)
- `/redoc` - ReDoc (alternative API documentation)

## Best Practices

1. **Always use async/await** for database operations
2. **Keep business logic in service layer**, not in API or repository
3. **Use soft delete by default**: Call `delete()` instead of `remove()`
4. **Define exceptions per module** in `exception/exception.py`
5. **Use type hints** everywhere for better IDE support
6. **Follow the module structure** consistently across all business modules
7. **Test via /docs** during development for quick feedback
