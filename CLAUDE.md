# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Game Bot System** for Yueliao (悦聊) chat platform, supporting Lucky8 and Liuhecai lottery games. The system is a **Python FastAPI backend** refactored from a Node.js version, featuring:

- **Admin Backend**: Management system for members, agents, reports (port 3003)
- **Bot Webhook Service**: Processes game messages from Yueliao chat groups
- **Dual Database Architecture**:
  - `users` table: Bot-managed game users (id + chat_id as composite PK)
  - `member_profiles`/`agent_profiles`: Admin-managed accounts with authentication

**Critical Architecture Note**: The admin backend and bot users are **intentionally separated**:
- Bot users are auto-created when joining game groups (`users` table)
- Admin accounts are manually created for backend management (`member_profiles` table)
- They can be linked via `user_id` but serve different purposes

## Development Commands

### Running the Application

```bash
# Start server (development)
python biz/application.py

# Start server (production with uvicorn)
uvicorn biz.application:app --host 0.0.0.0 --port 3003 --workers 4

# Initialize database tables
python -m base.init_db
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest test/test_members_api.py

# Run with verbose output and show print statements
pytest -v -s

# Run specific test function
pytest test/test_auth_api.py::TestAuthLogin::test_login_success

# Run tests with specific markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m db           # Database tests
```

### Linting and Type Checking

```bash
# Note: No pre-configured linting commands found
# The project uses Python type hints but no explicit lint/typecheck commands in config

# If you add linting, suggest:
# ruff check .           # Fast Python linter
# mypy biz/             # Type checking
```

## Architecture and Code Organization

### Layered Architecture

```
API Layer (biz/*/api/)
    ↓ handles HTTP, validates input
Service Layer (biz/*/service/)
    ↓ business logic, transactions
Repository Layer (biz/*/repo/)
    ↓ data access, SQL queries
Database (MySQL)
```

### Key Modules

**Game Module** (`biz/game/`):
- `service/game_service.py`: Core game logic (betting, balance, leaderboard)
- `scheduler/game_scheduler.py`: Auto-draw scheduling (5min for Lucky8, 24h for Liuhecai)
- `logic/`: Game-specific betting rules and odds calculation
- `webhook/webhook_api.py`: Handles events from Yueliao Bot API

**Users Module** (`biz/users/`):
- Split into **member** (players) and **agent** (distributors)
- Both have profiles, transactions, and account changes
- Uses **bcrypt** for password hashing

**Admin Module** (`biz/admin/`):
- JWT-based authentication
- Role-based access control (super_admin, distributor, agent, member)

**Reports Module** (`biz/reports/`):
- Financial summaries, win/loss reports, deposit/withdrawal tracking
- Pagination and cross-page statistics

### Dependency Injection

All services and repositories are managed via `dependency_injector`:

```python
# biz/containers.py defines the DI container
Container.user_service
Container.game_service
Container.member_repo
# etc.

# Usage in API endpoints:
from dependency_injector.wiring import inject, Provide

@inject
def get_member_service(service: MemberService = Depends(Provide[Container.member_service])):
    return service
```

### Database Schema Critical Notes

**Composite Primary Keys**:
- `users` table uses `(id, chat_id)` as composite PK
- This allows same user in multiple chats

**Field Name Mismatches** (fixed during debugging):
- `account_changes` table uses actual column names: `type`, `amount`, `created_at`, `note`
- NOT the model field names: `change_type`, `change_value`, `change_time`, `operator`
- `bet_orders` table uses `bet_result` not `win_amount`

**All tables are defined in** `biz/all_tables.py` for reference.

### External Integrations

**Yueliao Bot API Client** (`external/bot_api_client.py`):
- `BOT_API_BASE`: Running on port 65035
- Uses HMAC-SHA256 signature authentication
- Methods: `send_message()`, `send_image()`, `join_chat()`, `get_chat_members()`

**Draw API Clients** (`external/draw_api_client.py`):
- Fetches real lottery results from external APIs
- Separate APIs for Lucky8 and Liuhecai

### Testing Strategy

**Test Structure**:
- `test/conftest.py`: Shared fixtures (DB session, auth tokens)
- `test/test_*_crud.py`: Repository/service layer tests
- `test/test_*_api.py`: API endpoint tests
- `test/integration/`: Integration tests requiring external services

**Important Fixtures**:
- `auth_token`: JWT token for authenticated requests
- `auth_headers`: `{"Authorization": "Bearer <token>"}` for API calls

**Known Test Patterns**:
- Many tests use `AsyncClient` from `httpx`
- Database tests use real MySQL connection (not mocked)
- Some tests fail due to missing test data (not code issues)

## Common Development Tasks

### Adding a New API Endpoint

1. Define route in `biz/<module>/api/<module>_api.py`
2. Implement business logic in `biz/<module>/service/<module>_service.py`
3. Add database queries in `biz/<module>/repo/<module>_repo.py`
4. Register router in `biz/application.py`
5. Write tests in `test/test_<module>_api.py`

### Working with Database

**Using Raw SQL** (common pattern):
```python
from sqlalchemy import text

async def query_example(self):
    async with self._session_factory() as session:
        query = text("SELECT * FROM users WHERE chat_id = :chat_id")
        result = await session.execute(query, {"chat_id": chat_id})
        rows = result.fetchall()
        # Access via: row._mapping["column_name"]
```

**Critical**: Always use `CAST(field AS CHAR)` when comparing string fields in JOINs (MySQL strict mode requirement).

### Handling Exceptions

**Use UnifyException for business errors**:
```python
from base.exception import UnifyException
from base.error_codes import ErrorCode

# For 500 errors
raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)

# For 404 errors
raise UnifyException("Not found", biz_code=ErrorCode.DATA_NOT_FOUND, http_code=404)

# For 400 errors
raise UnifyException("Invalid input", biz_code=ErrorCode.BAD_REQUEST, http_code=400)
```

**Important**: All API exception handlers previously hard-coded `http_code=200` which was fixed. Always use appropriate HTTP status codes.

### Middleware Execution Order

Defined in `biz/application.py`:
1. RequestIDMiddleware (outermost)
2. LoggingMiddleware
3. Exception handlers (UnifyException, general Exception)

## Critical Configuration Files

- `.env`: Bot API credentials, ports, secrets
- `config.yaml`: Database connection strings
- `pytest.ini`: Test configuration
- `biz/all_tables.py`: Complete database schema reference

## Common Pitfalls

1. **Don't confuse users tables**: `users` (bot) vs `member_profiles` (admin) are separate
2. **Field name mismatches**: Always check actual DB column names in `biz/all_tables.py`
3. **Async context managers**: Always use `async with session_factory() as session:` not manual close
4. **HTTP status codes**: Don't return 200 for errors (was a previous bug)
5. **Composite PKs**: `users` table requires both `id` AND `chat_id`
6. **CAST in SQL**: Use `CAST(field AS CHAR)` for string comparisons to avoid MySQL warnings

## Environment Variables

Required in `.env`:
- `DATABASE_URI`: MySQL connection (asyncmy driver)
- `SYNC_DATABASE_URI`: Sync MySQL connection (pymysql driver)
- `BOT_API_BASE`, `BOT_API_KEY`, `BOT_API_SECRET`: Yueliao Bot API credentials
- `JWT_SECRET`: For admin authentication
- `WEBHOOK_PORT`: Default 3003
