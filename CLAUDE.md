# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Layout

This is a monorepo merged from previously separate repos (see recent merge commits). Each top-level directory is an independently buildable service with its own Dockerfile and dependencies:

- `backend/` — FastAPI HR/recruitment API (Python). Main entry: `app/main.py`, dev entry: `main_dev.py`. Uses MongoDB (Beanie ODM), Redis, MinIO, and Celery workers for CV processing.
- `frontend/` — React + TypeScript + Vite + Tailwind v3 + shadcn/ui. Source in `src/` with `pages/`, `components/`, `routes/`, `contexts/`, `hooks/`.
- `batch_manager/` — FastAPI service for CV-parse batch tasks (OpenAI batch API + MinIO storage). Entry: `app/main.py`. Owns its own MongoDB database `tyro_batch_manager`.
- `infra/` — Shared infra config; `infra/configs/.env` is the env file consumed by every service in the root `docker-compose.yml`.

The root `docker-compose.yml` is the canonical way to run the full stack. Per-service `docker-compose*.yml` files exist but are legacy/standalone — prefer the root one.

## Running the Stack

```bash
# Full stack (all services + mongo + redis + minio)
docker compose up -d
docker compose logs -f <service>     # backend | frontend | batch_manager | litellm | ...
docker compose down                  # add -v to wipe volumes
```

Ports: backend `8000`, batch_manager `8001`, frontend `5173`, mongo `27017`, redis `6379`, minio `9000`/`9001`, litellm `4000`. Python debugpy is exposed on `5678` (batch_manager) — set `WAIT_FOR_DEBUGGER=true` to pause until attach.

All Python services mount their source as a volume in dev (`Dockerfile.dev`), so code edits hot-reload without rebuilding.

## Per-Service Commands

### backend (Python)
```bash
cd backend
pip install -r requirements.txt
python main_dev.py                                # FastAPI dev server on :8000
celery -A app.conf.celery_config worker \
       --loglevel=info --queues=cv_processing,default   # background worker
pytest                                            # tests (pytest, pytest-asyncio)
black app/ && isort app/ && flake8 app/           # format + lint
```
API base: `http://localhost:8000/api/v1`, docs at `/docs`. Health: `/api/v1/health`.

### frontend (Node, pnpm)
```bash
cd frontend
pnpm install
pnpm dev          # vite dev server
pnpm build        # tsc -b && vite build
pnpm lint         # eslint .
pnpm preview
```
`openapi.json` at the frontend root is the contract from backend — regenerate when API changes.

### batch_manager
Same pattern as backend (FastAPI + uvicorn). Run via `docker compose` in practice.

## Architecture Notes

**Backend layering** (`backend/app/`): `api/` (FastAPI routers) → `service/` (business logic) → `repository/` (data access) → `entity/` (Beanie documents). DTOs live in `schema/`. `ai_agents/` holds LLM-driven analyzers (`job_position_analyzer.py`, `job_position_chat.py`). `workers/` inside backend contains Celery tasks. Database migrations auto-run on startup from `app/migration/`.

**Async tasks**: Celery (in `backend/`, broker = Redis) handles in-process background jobs queued directly from API requests. The `batch_manager` service brokers OpenAI batch API jobs and stores artifacts in MinIO bucket `batch-tasks`.

**Databases**: backend uses MongoDB db `tyro_db`; batch_manager uses `tyro_batch_manager` on the same mongo instance.

**Env config**: every service reads `infra/configs/.env` via docker-compose `env_file`. Service-specific overrides (e.g. `MONGODB_URL`, `MINIO_*`, debug flags) are set inline in `docker-compose.yml` and take precedence.

**LLM routing (LiteLLM proxy)**: a `litellm` container (`ghcr.io/berriai/litellm`, port `4000`) sits in front of every LLM provider. Configuration lives in `infra/litellm/config.yaml` — add or rename models there, no service rebuild needed. Provider keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `OLLAMA_BASE_URL`) and the proxy's `LITELLM_MASTER_KEY` come from `infra/configs/.env`. Local Ollama is reached via `host.docker.internal:11434` and exposed through the `ollama/*` wildcard route.

- **`backend/`** uses the proxy. All LLM calls flow through `app/ai_agents/model_factory.py::build_model`, which returns a single `pydantic_ai.OpenAIModel` pointed at `LITELLM_BASE_URL`. Per-request model selection: chat/analyzer DTOs accept an optional `model` field (e.g. `"gpt-4o"`, `"claude-sonnet-4-5"`, `"ollama/llama3.1"`); when omitted, falls back to `LITELLM_DEFAULT_CHAT_MODEL` / `LITELLM_DEFAULT_ANALYZER_MODEL`. The catalog endpoint `GET /api/v1/llm/models` proxies LiteLLM's `/v1/models` for the frontend picker.
- **Not yet migrated** — these still call OpenAI (or other providers) directly and should be routed through the proxy when touched:
  - `batch_manager/` — uses the OpenAI Batch API directly with `BATCH_OPENAI_API_KEY_*` keys. LiteLLM supports batch endpoints, but the rotation across multiple keys and MinIO artifact storage need design work first.
  - `frontend/` — model picker UI not yet implemented; the `GET /api/v1/llm/models` contract exists on the backend side and is ready to consume.

**Frontend routing**: React Router config in `src/routes/`; pages are `login`, `positions`, `position-details`, `add-position`. Auth/state via `src/contexts/`. UI primitives are shadcn/ui in `src/components/ui/`.
