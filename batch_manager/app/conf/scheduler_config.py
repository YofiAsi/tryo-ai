"""
Scheduler configuration for batch management operations.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings


class SchedulerSettings(BaseSettings):
    """
    Scheduler settings for batch management operations.
    
    Attributes:
    -----------
    SCHEDULER_ENABLED: bool
        Whether the scheduler should be enabled
    BATCH_CHECK_INTERVAL_MINUTES: int
        Interval in minutes for checking batch progress and completing tasks (sequential execution)
    BATCH_START_INTERVAL_MINUTES: int
        Interval in minutes for starting pending batches
    SCHEDULER_TIMEZONE: str
        Timezone for scheduler operations
    SCHEDULER_COALESCE: bool
        Whether to coalesce multiple pending executions of the same job
    SCHEDULER_MISFIRE_GRACE_TIME: int
        Grace time in seconds for missed job executions
    JOB_TIMEOUT_SECONDS: int
        Maximum time in seconds a job can run before being terminated
    JOB_EXECUTION_WARNING_THRESHOLD_SECONDS: int
        Time threshold in seconds after which a warning is logged for long-running jobs
    """
    
    SCHEDULER_ENABLED: bool = True
    BATCH_CHECK_INTERVAL_MINUTES: int = 1
    BATCH_START_INTERVAL_MINUTES: int = 1
    SCHEDULER_TIMEZONE: str = "UTC"
    SCHEDULER_COALESCE: bool = True
    SCHEDULER_MISFIRE_GRACE_TIME: int = 30
    JOB_TIMEOUT_SECONDS: int = 600  # 10 minutes default timeout
    JOB_EXECUTION_WARNING_THRESHOLD_SECONDS: int = 300  # Warn if job takes longer than 5 minutes

    class Config:
        env_prefix = "SCHEDULER_"
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
