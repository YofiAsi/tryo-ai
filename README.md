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
  <img width="100%" alt="download" src="https://github.com/user-attachments/assets/df7aac58-753d-45fe-a5fc-4800e6f52ad3" />
</p>

- **Add position** — multi-turn chat → structured job fields

<p align="center">
  <img width="100%" height="927" alt="download (1)" src="https://github.com/user-attachments/assets/ec2eda74-bf59-47fb-9532-6c5ba8eb8a97" />
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
