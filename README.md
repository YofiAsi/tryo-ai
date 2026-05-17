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

## Screenshots

<p align="center">
  <img width="100%" alt="Screenshot 2026-05-17 103526" src="https://github.com/user-attachments/assets/4264f4ad-2985-432c-9950-c46b80c53c75" />
</p>

<p align="center">
  <img width="100%" alt="Screenshot 2026-05-17 103613" src="https://github.com/user-attachments/assets/c3ca3bf1-327a-4419-bab1-3aa2c2658a48" />
</p>

<p align="center">
  <img width="100%" alt="Screenshot 2026-05-17 103124" src="https://github.com/user-attachments/assets/62150002-aae9-41d5-b5df-0ea6e989b4d9" />
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
