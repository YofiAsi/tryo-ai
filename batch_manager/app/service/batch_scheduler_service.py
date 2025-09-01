"""
BatchSchedulerService for managing scheduled batch operations.

This service handles the periodic execution of batch management tasks including:
- Starting pending batches
- Checking progress of in-progress batches  
- Checking and completing batch tasks
"""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, Dict, List

from apscheduler.executors.asyncio import AsyncIOExecutor  # type: ignore[import-untyped]
from apscheduler.jobstores.memory import MemoryJobStore  # type: ignore[import-untyped]
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]

from app.conf.scheduler_config import SchedulerSettings

if TYPE_CHECKING:
    from app.service.manager_service import ManagerService

_log = logging.getLogger(__name__)


class BatchSchedulerService:
    """
    Service responsible for scheduling and managing periodic batch operations.
    
    This service follows DDD principles by encapsulating the scheduling domain logic
    and providing a clean interface for batch management operations.
    """
    
    def __init__(self, manager_service: ManagerService) -> None:
        """
        Initialize the batch scheduler service.
        
        Args:
            manager_service: The manager service instance for executing batch operations
        """
        self._manager_service = manager_service
        self._settings = SchedulerSettings()
        self._scheduler: AsyncIOScheduler | None = None
        self._is_running = False
        
        # Job execution tracking
        self._job_execution_times: Dict[str, Dict[str, Any]] = {}
        self._running_jobs: set[str] = set()
        
        # Configure scheduler with production-ready settings
        self._configure_scheduler()
    
    def _configure_scheduler(self) -> None:
        """Configure the AsyncIO scheduler with production-ready settings."""
        job_stores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': AsyncIOExecutor()
        }
        
        job_defaults = {
            'coalesce': self._settings.SCHEDULER_COALESCE,
            'misfire_grace_time': self._settings.SCHEDULER_MISFIRE_GRACE_TIME,
            'max_instances': 1  # Prevent concurrent executions of the same job
        }
        
        self._scheduler = AsyncIOScheduler(
            jobstores=job_stores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self._settings.SCHEDULER_TIMEZONE
        )
    
    async def start(self) -> None:
        """
        Start the scheduler and register all batch management jobs.
        
        This method is idempotent and can be called multiple times safely.
        """
        if not self._settings.SCHEDULER_ENABLED:
            _log.info("Scheduler is disabled via configuration")
            return
            
        if self._is_running:
            _log.warning("Scheduler is already running")
            return
        
        if not self._scheduler:
            _log.error("Scheduler not properly configured")
            return
        
        try:
            # Register periodic jobs
            self._register_jobs()
            
            # Start the scheduler
            self._scheduler.start()
            self._is_running = True
            
            _log.info(
                f"Batch scheduler started successfully with jobs: "
                f"batch_check_and_tasks_sequence_interval={self._settings.BATCH_CHECK_INTERVAL_MINUTES}min, "
                f"batch_start_interval={self._settings.BATCH_START_INTERVAL_MINUTES}min"
            )
            
        except Exception as e:
            _log.error(f"Failed to start batch scheduler: {str(e)}")
            raise
    
    async def stop(self) -> None:
        """
        Stop the scheduler gracefully.
        
        This method waits for all running jobs to complete before shutting down.
        """
        if not self._is_running or not self._scheduler:
            _log.info("Scheduler is not running")
            return
        
        try:
            self._scheduler.shutdown(wait=True)
            self._is_running = False
            _log.info("Batch scheduler stopped successfully")
            
        except Exception as e:
            _log.error(f"Error stopping batch scheduler: {str(e)}")
            raise
    
    def _register_jobs(self) -> None:
        """Register all periodic batch management jobs."""
        if not self._scheduler:
            raise RuntimeError("Scheduler not initialized")
        
        # Job 1: Start pending batches
        self._scheduler.add_job(
            func=self._safe_start_pending_batches,
            trigger='interval',
            minutes=self._settings.BATCH_START_INTERVAL_MINUTES,
            id='start_pending_batches',
            name='Start Pending Batches',
            replace_existing=True
        )
        
        # Job 2: Check on in-progress batches and then check tasks (dependent execution)
        self._scheduler.add_job(
            func=self._safe_check_batches_and_tasks_sequence,
            trigger='interval',
            minutes=self._settings.BATCH_CHECK_INTERVAL_MINUTES,
            id='check_batches_and_tasks_sequence',
            name='Check Batches In Progress and Complete Tasks',
            replace_existing=True
        )
        
        _log.info("All batch management jobs registered successfully")
    
    def _is_job_running(self, job_id: str) -> bool:
        """Check if a job is currently running."""
        return job_id in self._running_jobs
    
    def _start_job_tracking(self, job_id: str) -> None:
        """Start tracking job execution."""
        self._running_jobs.add(job_id)
        self._job_execution_times[job_id] = {
            'start_time': time.time(),
            'start_datetime': datetime.now(timezone.utc).isoformat(),
            'status': 'running'
        }
        _log.info(f"Job '{job_id}' started at {self._job_execution_times[job_id]['start_datetime']}")
    
    def _finish_job_tracking(self, job_id: str, success: bool = True) -> None:
        """Finish tracking job execution."""
        self._running_jobs.discard(job_id)
        if job_id in self._job_execution_times:
            end_time = time.time()
            start_time = self._job_execution_times[job_id]['start_time']
            execution_time = end_time - start_time
            
            self._job_execution_times[job_id].update({
                'end_time': end_time,
                'end_datetime': datetime.now(timezone.utc).isoformat(),
                'execution_time_seconds': execution_time,
                'status': 'completed' if success else 'failed'
            })
            
            # Log execution time and warn if it's taking too long
            if execution_time > self._settings.JOB_EXECUTION_WARNING_THRESHOLD_SECONDS:
                _log.warning(
                    f"Job '{job_id}' took {execution_time:.2f} seconds to complete "
                    f"(threshold: {self._settings.JOB_EXECUTION_WARNING_THRESHOLD_SECONDS}s)"
                )
            else:
                _log.info(f"Job '{job_id}' completed in {execution_time:.2f} seconds")
    
    async def _execute_with_timeout_and_tracking(
        self, 
        job_id: str, 
        job_func: Callable[..., Any], 
        *args: Any, 
        **kwargs: Any
    ) -> None:
        """
        Execute a job with timeout and execution tracking.
        
        Args:
            job_id: Unique identifier for the job
            job_func: The async function to execute
            *args: Arguments for the job function
            **kwargs: Keyword arguments for the job function
        """
        # Check if job is already running
        if self._is_job_running(job_id):
            _log.warning(f"Job '{job_id}' is already running, skipping this execution")
            return
        
        # Start tracking
        self._start_job_tracking(job_id)
        
        try:
            # Execute with timeout
            await asyncio.wait_for(
                job_func(*args, **kwargs),
                timeout=self._settings.JOB_TIMEOUT_SECONDS
            )
            self._finish_job_tracking(job_id, success=True)
            
        except asyncio.TimeoutError:
            _log.error(
                f"Job '{job_id}' timed out after {self._settings.JOB_TIMEOUT_SECONDS} seconds"
            )
            self._finish_job_tracking(job_id, success=False)
            
        except Exception as e:
            _log.error(f"Job '{job_id}' failed with error: {str(e)}")
            self._finish_job_tracking(job_id, success=False)
    
    async def _safe_start_pending_batches(self) -> None:
        """
        Safely execute the start pending batches operation with timeout and tracking.
        """
        await self._execute_with_timeout_and_tracking(
            job_id='start_pending_batches',
            job_func=self._manager_service.start_pending_batches
        )
    
    async def _safe_check_batches_and_tasks_sequence(self) -> None:
        """
        Safely execute the sequential batch checking operations with timeout and tracking.
        """
        await self._execute_with_timeout_and_tracking(
            job_id='check_batches_and_tasks_sequence',
            job_func=self._execute_batches_and_tasks_sequence
        )
    
    async def _execute_batches_and_tasks_sequence(self) -> None:
        """
        Execute the sequential batch checking operations.
        
        This method first checks batches in progress, then checks and completes tasks.
        The operations are dependent - task checking only happens after batch checking completes.
        """
        _log.debug("Executing scheduled job sequence: check_batches_and_tasks_sequence")
        
        # Step 1: Check on batches in progress
        _log.debug("Step 1: Checking batches in progress")
        await self._manager_service.update_non_terminal_state_batches()
        
        # Step 2: Check and complete batch tasks (dependent on step 1)
        _log.debug("Step 2: Checking and completing batch tasks")
        await self._manager_service.check_and_complete_batch_tasks()
        
        _log.debug("Completed scheduled job sequence: check_batches_and_tasks_sequence")
    
    def get_job_status(self) -> Dict[str, Any]:
        """
        Get the current status of all scheduled jobs.
        
        Returns:
            Dictionary containing job status information for monitoring purposes
        """
        if not self._scheduler or not self._is_running:
            return {
                "scheduler_status": "stopped", 
                "jobs": {}, 
                "running_jobs": [],
                "execution_history": {},
                "settings": {}
            }
        
        jobs_info = {}
        for job in self._scheduler.get_jobs():
            job_id = job.id
            jobs_info[job_id] = {
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
                "is_running": self._is_job_running(job_id)
            }
        
        return {
            "scheduler_status": "running",
            "jobs": jobs_info,
            "running_jobs": list(self._running_jobs),
            "execution_history": self._get_recent_execution_history(),
            "settings": {
                "batch_check_and_tasks_sequence_interval_minutes": self._settings.BATCH_CHECK_INTERVAL_MINUTES,
                "batch_start_interval_minutes": self._settings.BATCH_START_INTERVAL_MINUTES,
                "job_timeout_seconds": self._settings.JOB_TIMEOUT_SECONDS,
                "job_execution_warning_threshold_seconds": self._settings.JOB_EXECUTION_WARNING_THRESHOLD_SECONDS,
                "timezone": self._settings.SCHEDULER_TIMEZONE,
                "note": "check_and_complete_tasks runs sequentially after check_batches_in_progress"
            }
        }
    
    def _get_recent_execution_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent job execution history.
        
        Args:
            limit: Maximum number of recent executions per job to return
            
        Returns:
            Dictionary with job execution history
        """
        history: Dict[str, Any] = {}
        for job_id, execution_data in self._job_execution_times.items():
            # Add execution data (you might want to keep multiple executions in the future)
            history[job_id] = execution_data
            
        return history
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the scheduler for monitoring.
        
        Returns:
            Dictionary containing health information
        """
        current_time = time.time()
        long_running_jobs: List[Dict[str, Any]] = []
        
        for job_id in self._running_jobs:
            if job_id in self._job_execution_times:
                start_time = self._job_execution_times[job_id]['start_time']
                runtime = current_time - start_time
                
                if runtime > self._settings.JOB_EXECUTION_WARNING_THRESHOLD_SECONDS:
                    long_running_jobs.append({
                        'job_id': job_id,
                        'runtime_seconds': runtime,
                        'start_time': self._job_execution_times[job_id]['start_datetime']
                    })
        
        health_status = "healthy"
        if long_running_jobs:
            health_status = "warning" if len(long_running_jobs) < 2 else "critical"
        
        return {
            "health_status": health_status,
            "scheduler_running": self._is_running,
            "active_jobs_count": len(self._running_jobs),
            "long_running_jobs": long_running_jobs,
            "total_job_executions": len(self._job_execution_times),
            "settings_check": {
                "timeout_configured": self._settings.JOB_TIMEOUT_SECONDS > 0,
                "warning_threshold_configured": self._settings.JOB_EXECUTION_WARNING_THRESHOLD_SECONDS > 0
            }
        }
    
    def cleanup_old_execution_history(self, max_age_hours: int = 24) -> int:
        """
        Clean up old job execution history to prevent memory leaks.
        
        Args:
            max_age_hours: Maximum age in hours for keeping execution history
            
        Returns:
            Number of cleaned up entries
        """
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)  # Convert hours to seconds
        
        cleaned_count = 0
        job_ids_to_remove = []
        
        for job_id, execution_data in self._job_execution_times.items():
            # Skip currently running jobs
            if job_id in self._running_jobs:
                continue
                
            # Remove old completed/failed jobs
            if ('end_time' in execution_data and 
                execution_data['end_time'] < cutoff_time):
                job_ids_to_remove.append(job_id)
                cleaned_count += 1
        
        # Remove the old entries
        for job_id in job_ids_to_remove:
            del self._job_execution_times[job_id]
        
        if cleaned_count > 0:
            _log.info(f"Cleaned up {cleaned_count} old job execution records")
        
        return cleaned_count
    
    @property
    def is_running(self) -> bool:
        """Check if the scheduler is currently running."""
        return self._is_running
