#!/usr/bin/env python3
"""
Celery Worker Startup Script for HR Backend API

This script starts the Celery worker for processing background tasks.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.conf.celery_config import celery_app

if __name__ == "__main__":
    # Set environment variables if not already set
    os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
    os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    print("Starting Celery worker for HR Backend API...")
    print(f"Broker URL: {os.getenv('CELERY_BROKER_URL')}")
    print(f"Result Backend: {os.getenv('CELERY_RESULT_BACKEND')}")
    
    # Start the worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=2",
        "--queues=cv_processing,default",
        "--hostname=hr-backend-worker@%h"
    ])
