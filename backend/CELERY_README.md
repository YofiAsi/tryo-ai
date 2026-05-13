# Celery Worker Setup for HR Backend API

This document explains how to set up and use the Celery worker system for processing background tasks.

## Overview

The system now includes Celery workers for processing CV processing tasks asynchronously. When a task is created through the API, it's automatically queued for background processing.

## Prerequisites

1. **Redis Server**: Required as the message broker and result backend
2. **Python Dependencies**: Install the required packages

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_celery.txt
```

### 2. Start Redis Server

#### Option A: Using Docker (Recommended for development)

```bash
docker-compose -f docker-compose.redis.yml up -d
```

This will start:
- Redis server on port 6379
- Flower (Celery monitoring) on port 5555

#### Option B: Install Redis locally

- **Windows**: Use WSL2 or Redis for Windows
- **macOS**: `brew install redis`
- **Linux**: `sudo apt-get install redis-server`

### 3. Environment Variables

Set these environment variables (or they will use defaults):

```bash
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

## Running the System

### 1. Start the Celery Worker

```bash
python celery_worker.py
```

Or using Celery directly:

```bash
celery -A app.conf.celery_config worker --loglevel=info --queues=cv_processing,default
```

### 2. Start the FastAPI Application

```bash
python main_dev.py
```

## API Usage

### Creating a CV Processing Task

```bash
POST /admin/tasks
Content-Type: application/json

{
  "type": "cv_processing",
  "data": {
    "candidates_ids": [
      "123e4567-e89b-12d3-a456-426614174000",
      "987fcdeb-51a2-43d1-9f12-345678901234"
    ]
  }
}
```

### Monitoring Task Progress

```bash
GET /admin/tasks/{task_id}
```

The task status will automatically update as the Celery worker processes it:
- `pending` → `processing` → `completed`/`failed`

## Task Processing Flow

1. **API Request**: Client creates a task via `/admin/tasks`
2. **Database Record**: Task is saved to database with `pending` status
3. **Celery Queue**: Task is queued for background processing
4. **Worker Processing**: Celery worker picks up the task and updates progress
5. **Status Updates**: Task status and progress are updated in real-time
6. **Completion**: Task status is set to `completed` or `failed`

## Monitoring

### Flower Dashboard

Access the Flower dashboard at `http://localhost:5555` to monitor:
- Active workers
- Task queues
- Task execution history
- Worker performance

### Logs

Monitor the Celery worker logs for detailed task execution information:

```bash
tail -f celery_worker.log
```

## Configuration

### Celery Settings

Key configuration options in `app/conf/celery_config.py`:

- **Task Time Limits**: 30 minutes hard limit, 25 minutes soft limit
- **Worker Concurrency**: 2 workers by default
- **Queue Routing**: CV processing tasks go to dedicated queue
- **Result Backend**: Redis for storing task results

### Customization

To add new task types:

1. Add new enum values in `app/entity/task_entity.py`
2. Create new worker functions in `app/workers/`
3. Update the task service to handle new types
4. Add new queue configurations if needed

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis server is running
   - Check connection URL in environment variables

2. **Worker Not Processing Tasks**
   - Verify worker is running and connected to Redis
   - Check queue names match between API and worker

3. **Task Stuck in Pending**
   - Check worker logs for errors
   - Verify task routing configuration

### Debug Mode

Enable debug logging:

```bash
celery -A app.conf.celery_config worker --loglevel=debug
```

## Production Considerations

1. **Multiple Workers**: Scale workers based on load
2. **Redis Persistence**: Enable Redis persistence for reliability
3. **Monitoring**: Use Flower or similar tools for production monitoring
4. **Error Handling**: Implement proper error handling and retry logic
5. **Security**: Secure Redis access in production environments

## Development Workflow

1. Start Redis: `docker-compose -f docker-compose.redis.yml up -d`
2. Start Worker: `python celery_worker.py`
3. Start API: `python main_dev.py`
4. Create tasks via API
5. Monitor progress in Flower dashboard
6. Check worker logs for debugging
