# Task 1 Progress — GUARDIAN Phase 2 Backend Core

## Status
**ALL STEPS COMPLETE. Task 1 Phase 2 Backend — DONE.**

### Step 6: Apply migration ✅ (2026-04-21)
- Reset alembic stamp (DB had been stamped without schema applied)
- `alembic upgrade head` applied 0001 + 0002 cleanly
- All 8 tables confirmed: organizations, assets, asset_fingerprints, tasks, scan_runs, violations, dmca_notices, users

### Step 7: Full test suite ✅ (2026-04-21)
- 11/11 PASSED (10 existing + test_create_user)

### Step 8: Git commit ✅ (2026-04-21)
- Committed: User model, migration 0002, updated __init__.py, test appended

## Completed Steps

### Step 1: Append test to apps/api/tests/test_db_models.py ✅
Added `test_create_user` function that:
- Creates an Organization
- Creates a User with org_id, email, and hashed_password
- Validates user.id and is_active=True

### Step 2: Create apps/api/models/user.py ✅
Created User ORM model with:
- id (UUID, primary key)
- org_id (UUID, FK to organizations)
- email (String 255, unique, indexed)
- hashed_password (String 255)
- is_active (Boolean, default True)
- created_at (DateTime with timezone, server default now())
- organization relationship to Organization

### Step 3: Update apps/api/models/__init__.py ✅
Added User import and added "User" to __all__ list

### Step 4: Run test to confirm ✅
Test `test_create_user` **PASSED** without errors
- The conftest.py fixture creates tables from ORM models, so test passes immediately

### Step 5: Create migration apps/api/db/migrations/versions/0002_add_users.py ✅
Created migration with:
- revision = "0002"
- down_revision = "b47f479c9504" (the actual revision ID from 0001_initial_schema.py)
- upgrade() creates users table with all columns and ix_users_email unique index
- downgrade() drops index and table

## Files Modified/Created
1. `apps/api/models/user.py` (NEW)
2. `apps/api/models/__init__.py` (MODIFIED)
3. `apps/api/db/migrations/versions/0002_add_users.py` (NEW)
4. `apps/api/tests/test_db_models.py` (MODIFIED)

---

## Next Task: Task 2 Phase 2 — Auth / JWT Layer
Implement authentication endpoints (register, login, token refresh) using JWT.
Files to create: `routers/auth.py`, `services/auth_service.py`, `schemas/auth.py`
