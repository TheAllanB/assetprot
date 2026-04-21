# GUARDIAN Phase 2 Backend — Progress

---

## Task 1: User ORM Model + Migration ✅ COMPLETE (2026-04-21)

- `apps/api/models/user.py` — User ORM model (id, org_id FK, email, hashed_password, is_active, created_at)
- `apps/api/models/__init__.py` — User registered in __all__
- `apps/api/db/migrations/versions/0002_add_users.py` — Alembic migration (revision 0002, down_revision b47f479c9504)
- `apps/api/tests/test_db_models.py` — test_create_user added
- All 8 tables live in PostgreSQL; 11/11 tests passing
- Commit: `5fd6330`

---

## Task 2: Auth / JWT Layer 🔄 IN PROGRESS

### Design ✅ (2026-04-21)
- Spec: `docs/superpowers/specs/2026-04-21-auth-jwt-design.md` (commit `b20429b`)
- Approach: JSON body tokens (access 15 min + refresh 7 days), no cookies in MVP
- `HTTPBearer` scheme (not OAuth2PasswordBearer — login accepts JSON not form data)

### Implementation ⏳ PENDING
Files to create:
- `apps/api/schemas/auth.py` — RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserResponse
- `apps/api/core/security.py` — hash_password, verify_password, create_access_token, create_refresh_token, decode_token
- `apps/api/services/auth_service.py` — AuthService (register, login, refresh, get_me)
- `apps/api/dependencies/auth.py` — get_current_user Depends()
- `apps/api/routers/auth.py` — 4 thin route handlers
- Update `apps/api/main.py` — include_router(auth_router, prefix="/auth")
- Update `apps/api/requirements.txt` — add passlib[bcrypt], python-jose[cryptography]
- `apps/api/tests/test_auth.py` — 9 tests (register, login, refresh, me)

Token payload: `{ "sub": "<user_id>", "org_id": "<org_id>", "type": "access"|"refresh", "exp": ... }`
Signing: HS256, key: `settings.jwt_secret_key` (already in Settings)

### Resumption Prompt
See bottom of file.

---

## DB State
- PostgreSQL running locally on port 5432
- `DATABASE_URL=postgresql+asyncpg://guardian:changeme_dev@localhost:5432/guardian`
- Run migrations with: `DATABASE_URL="postgresql+asyncpg://guardian:changeme_dev@localhost:5432/guardian" alembic upgrade head`
- Run tests with: `DATABASE_URL="postgresql+asyncpg://guardian:changeme_dev@localhost:5432/guardian" pytest tests/ -v`

---

## Resumption Prompt (Next Session)

> Continue GUARDIAN Phase 2 Backend — Task 2: Auth/JWT Layer implementation.
>
> Design is approved and spec is at `docs/superpowers/specs/2026-04-21-auth-jwt-design.md`. Read progress.md and the spec before starting.
>
> Start by invoking the `superpowers:writing-plans` skill to create a step-by-step implementation plan, then implement using TDD (`superpowers:test-driven-development`).
>
> Key context:
> - Stack: FastAPI + SQLAlchemy async + PostgreSQL
> - `settings.jwt_secret_key` already exists in `core/config.py`
> - `get_async_session()` is the DB dependency in `db/session.py`
> - Router → Service → Dependency pattern (see CLAUDE.md)
> - Tokens returned as JSON body (not cookies)
> - Use `HTTPBearer` not `OAuth2PasswordBearer`
> - No routers/, services/, schemas/, dependencies/ directories exist yet — create them
> - PostgreSQL is on localhost:5432; prefix alembic/pytest commands with `DATABASE_URL="postgresql+asyncpg://guardian:changeme_dev@localhost:5432/guardian"`
> - 11/11 tests currently passing — do not regress
