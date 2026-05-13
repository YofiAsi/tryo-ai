# AGENTS.md

## Cursor Cloud specific instructions

### Services overview

| Service | Port | Purpose |
|---|---|---|
| **backend** (FastAPI) | 8000 | HR/recruitment API — auth, job positions, candidates, AI agents |
| **frontend** (Vite + React) | 5173 | SPA — positions list, position details, add-position, login |
| **batch_manager** (FastAPI) | 8001 | Optional — OpenAI batch API CV-parse jobs |
| **MongoDB** | 27017 | Primary data store (run via Docker: `mongodb/mongodb-atlas-local`) |
| **Redis** | 6379 | Celery broker/result backend (run via Docker: `redis:7-alpine`) |

### Starting infrastructure (MongoDB + Redis)

```bash
docker run -d --name tyro-mongo -p 27017:27017 mongodb/mongodb-atlas-local
docker run -d --name tyro-redis -p 6379:6379 redis:7-alpine redis-server --appendonly yes
```

The MongoDB Atlas Local image uses a replica set whose member hostname is the container ID. You **must** resolve it from the host. Either:
- Add the container hostname to `/etc/hosts`: get it with `docker exec tyro-mongo mongosh --eval "rs.status().members[0].name"` (the part before `:27017`), then `echo "127.0.0.1 <hostname>" | sudo tee -a /etc/hosts`, **or**
- Use `DB_MONGODB_URI="mongodb://localhost:27017/?directConnection=true"` to bypass replica set discovery entirely (preferred for local dev).

### Starting the backend

```bash
cd /workspace/backend
source .venv/bin/activate
DEV_AUTH_BYPASS=true \
DB_MONGODB_URI="mongodb://localhost:27017/?directConnection=true" \
DB_DATABASE_NAME=tyro_db \
SENTRY_ENABLE=false \
LITELLM_BASE_URL=http://localhost:4000 \
PYTHONPATH=/workspace/backend \
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check: `curl http://localhost:8000/api/v1/health` -> `{"status":"UP"}`
API docs: `http://localhost:8000/api/v1/docs`

### Starting the frontend

```bash
cd /workspace/frontend
VITE_DEV_AUTH_BYPASS=true VITE_API_BASE_URL=http://localhost:8000 pnpm dev --host 0.0.0.0 --port 5173
```

### Dev auth bypass

Set `DEV_AUTH_BYPASS=true` (backend) and `VITE_DEV_AUTH_BYPASS=true` (frontend) to skip Google OAuth and auto-create/login as `dev@local.dev` (Admin role). Both must be set for the flow to work end-to-end.

### Lint and test commands

- **Backend lint**: `cd backend && source .venv/bin/activate && flake8 app/` (also: `black app/`, `isort app/`)
- **Frontend lint**: `cd frontend && pnpm lint`
- **Frontend build**: `cd frontend && pnpm build` (note: has a pre-existing TS error on `step2-summary.tsx`)
- **Backend tests**: `cd backend && source .venv/bin/activate && pytest` (no tests exist yet)

### Gotchas

- The `.env` file at `infra/configs/.env` is gitignored and must be created locally. It needs at minimum placeholder values for `DB_HOST`, `DB_PORT`, `DB_DATABASE_NAME`, `LITELLM_MASTER_KEY`, and `SENTRY_ENABLE=false`.
- `pnpm install` in `frontend/` blocks on esbuild build scripts by default in pnpm v10+. The `pnpm.onlyBuiltDependencies` field in `package.json` allows esbuild to run its postinstall.
- Python venv is at `backend/.venv/` — always activate it before running backend commands.
- LiteLLM proxy (port 4000) is optional for basic CRUD operations but required for AI agent features. Backend starts fine without it connected.
