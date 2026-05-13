<div align="center">

# Tyro

HR / recruitment monorepo — positions, AI-assisted drafting, CVs, Celery workers, OpenAI Batch jobs.

</div>

## Stack

- **`backend/`** — FastAPI, MongoDB (Beanie), Redis, Celery, LLM agents (LiteLLM)
- **`frontend/`** — React, TypeScript, Vite, Tailwind, shadcn/ui
- **`batch_manager/`** — OpenAI Batch JSONL pipeline, MinIO, scheduler
- **`infra/`** — shared config (e.g. LiteLLM)

**Run:** root `docker-compose.yml` · **Details:** [`CLAUDE.md`](./CLAUDE.md)

## Screenshots (dark theme)

<p align="center">
  <img src="./docs/assets/add-position-chat.png" alt="Add Position chat" width="920">
</p>

- **Add position** — multi-turn chat → structured job fields

<p align="center">
  <img src="./docs/assets/position-details.png" alt="Position details" width="920">
</p>

- **Position** — overview + matched candidates table

## Flow

```mermaid
flowchart LR
  A[Create job position<br/>chat + analyze] --> B[Save role +<br/>JobTournament]
  B --> C[Tournament<br/>LLM comparisons<br/>batch / workers]
  C --> D[Results<br/>rank · wins · reasoning]
```

**TLDR:** comparisons → ranked candidates (`wins` / `rank` / `reasoning`). Heavy runs → JSONL chunks → MinIO → OpenAI Batch → scheduler until done.
