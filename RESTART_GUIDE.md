# GUARDIAN: Restart Guide

**Last Updated:** 2026-04-28
**Checkpoint:** Core Backend + Frontend MVP Complete

---

## Quick Start from Checkpoint

### Prerequisites
```bash
# Ensure Docker and docker-compose are installed
# Ensure Python 3.11+ is available
# Ensure Node.js 18+ is available
```

### 1. Start the Stack
```bash
# From project root
docker compose up --build -d

# Wait for services to be ready (~30 seconds)
curl http://localhost:8000/health
```

### 2. Seed Demo Data
```bash
# Seed the database with demo data
cd apps/api
python -m db.seed

# Or let it seed automatically on startup (non-production)
```

### 3. Test Authentication
```bash
# Login with demo credentials
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","password":"demo123"}'

# Returns: {access_token, refresh_token}
```

### 4. Test API Calls
```bash
TOKEN="your-access-token"

# List assets
curl http://localhost:8000/api/v1/assets \
  -H "Authorization: Bearer $TOKEN"

# List violations
curl http://localhost:8000/api/v1/violations \
  -H "Authorization: Bearer $TOKEN"

# Get single violation
curl http://localhost:8000/api/v1/violations/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Test WebSocket
```bash
# Using wscat or similar
wscat -c ws://localhost:8000/ws/alerts/demo-user

# Should receive: {"type":"pong"}
# Send: ping
```

### 6. Frontend
```bash
# Start frontend
cd apps/web
npm run dev

# Open http://localhost:3000
# Login: admin@demo.com / demo123
# View dashboard with threat map
```

---

## What Was Implemented

### Backend (Python/FastAPI)
| Feature | Status | File |
|---------|--------|------|
| Health Check | ✅ | main.py |
| JWT Auth | ✅ | core/security.py |
| Asset CRUD | ✅ | routers/assets.py |
| Violation CRUD | ✅ | routers/violations.py |
| Scan Run endpoints | ✅ | routers/scan_runs.py |
| Agent traces | ✅ | scan_runs.py + scan_run_repo.py |
| WebSocket alerts | ✅ | routers/ws.py |
| Fingerprinting | ✅ | tasks/fingerprint_task.py |
| Qdrant storage | ✅ | ml/qdrant_store.py |
| Demo data | ✅ | db/seed.py |

### Frontend (Next.js)
| Feature | Status | File |
|---------|--------|------|
| Login page | ✅ | app/login/page.tsx |
| Register page | ✅ | app/register/page.tsx |
| Dashboard | ✅ | app/dashboard/page.tsx |
| Assets list | ✅ | app/dashboard/assets/page.tsx |
| Upload | ✅ | app/dashboard/upload/page.tsx |
| Violations list | ✅ | app/dashboard/violations/page.tsx |
| Threat Map | ✅ | components/ThreatMap.tsx |

### Models
| Model | Fields |
|-------|-------|
| Organization | id, name, plan |
| User | id, org_id, email, hashed_password |
| Asset | id, org_id, title, content_type, status |
| AssetFingerprint | id, asset_id, phash, whash, clip_embedding |
| Violation | id, org_id, asset_id, discovered_url, platform, confidence |
| ScanRun | id, org_id, asset_id, status, agent_trace_log |

---

## Known Issues / TODOs

1. **Database migrations** - Need to run alembic to add org_id columns
2. **CLIP model loading** - Downloads on first run (~500MB)
3. **WebSocket auth** - Currently unauthenticated
4. **DMCA generation** - Basic template, needs more fields

---

## To Add Next (Priority Order)

### Tier 1: Demo Essentials
1. [ ] Run database migrations for new org_id fields
2. [ ] Connect seed script to startup
3. [ ] Add more test violations to demo data
4. [ ] Test upload + fingerprint flow

### Tier 2: Polish
5. [ ] Add per-modality scores to ViolationResponse
6. [ ] Add watermark extraction confidence
7. [ ] Add agent trace visualization
8. [ ] Structured logging

### Tier 3: Advanced
9. [ ] Threat map with Mapbox GL
10. [ ] Real-time WebSocket updates on violations
11. [ ] Request signing
12. [ ] Anomaly detection on asset list

---

## API Reference

### Health
```bash
GET /health
# Returns: {status, services: {database, redis, qdrant, ml_models}}
```

### Auth
```bash
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /auth/me
```

### Assets
```bash
GET  /api/v1/assets
POST /api/v1/assets
GET  /api/v1/assets/:id
```

### Violations
```bash
GET  /api/v1/violations
GET  /api/v1/violations/:id
POST /api/v1/violations
```

### Scan Runs
```bash
GET  /api/v1/scan-runs
GET  /api/v1/scan-runs/:id
GET  /api/v1/scan-runs/:id/trace
POST /api/v1/scan-runs
```

### DMCA
```bash
POST /api/v1/dmca
```

### WebSocket
```bash
WS /ws/alerts/:user_id
WS /ws/org/:org_id
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.11 |
| ORM | SQLAlchemy async |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Vector DB | Qdrant |
| Tasks | Celery |
| ML Models | CLIP + Chromaprint |
| Auth | JWT |
| Frontend | Next.js 14 + TypeScript |
| Styling | Tailwind CSS |
| Container | Docker Compose |

---

## Troubleshooting

### Health Check Returns 503
- Check PostgreSQL is running: `docker compose ps`
- Check Redis is running: `docker compose ps`
- Check Qdrant is running: `docker compose ps`

### Model Loading Fails
- First run downloads CLIP model (~500MB)
- Check network connection

### Database Errors
- Run migrations: `cd apps/api && alembic upgrade head`
- Or: `cd apps/api && python -m db.seed` (creates tables)

### Frontend Errors
- Check npm install: `cd apps/web && npm install`
- Check .env file exists with API URL

---

## Questions?

See: `PROGRESS.md` for detailed implementation history
See: `CLAUDE.md` for project context