"""
BatchDownloadQueueService for managing parallel batch file downloads.

This service continuously scans the repository for batches that need their files downloaded
and stored, processing them in parallel to maximize throughput while respecting system limits.
"""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from app.entity.batch_entity import Batch, BatchStatus

if TYPE_CHECKING:
    from beanie import PydanticObjectId
    from app.service.batch_service import BatchService
    from app.repository.batch_repository import BatchRepository

# Constants for service management
DEFAULT_MAX_CONCURRENT_DOWNLOADS = 5
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY_SECONDS = 2
DEFAULT_SCAN_INTERVAL_SECONDS = 30.0  # How often to scan for new batches

_log = logging.getLogger(__name__)


class BatchDownloadQueueService:
    """
    Singleton service for managing parallel batch file downloads.
    
    This service continuously scans the repository for batches that need their files downloaded
    and processes them in parallel with configurable concurrency limits.
    
    Features:
    - Singleton pattern for application-wide service management
    - Configurable concurrent download limits
    - Retry logic for failed downloads
    - Health monitoring and status reporting
    - Graceful shutdown handling
    - Repository-based batch discovery
    """
    
    _instance: Optional[BatchDownloadQueueService] = None
    _lock = asyncio.Lock()
    
    def __new__(cls, *args: Any, **kwargs: Any) -> BatchDownloadQueueService:
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        batch_service: BatchService,
        batch_repository: BatchRepository,
        max_concurrent_downloads: int = DEFAULT_MAX_CONCURRENT_DOWNLOADS,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
        retry_delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS,
        scan_interval_seconds: float = DEFAULT_SCAN_INTERVAL_SECONDS,
    ) -> None:
        """
        Initialize the batch download queue service.
        
        Args:
            batch_service: Service for batch operations
            batch_repository: Repository for batch data access
            max_concurrent_downloads: Maximum concurrent downloads allowed
            retry_attempts: Number of retry attempts for failed downloads
            retry_delay_seconds: Delay between retry attempts
            scan_interval_seconds: Interval for scanning repository for new batches
        """
        # Prevent re-initialization of singleton
        if hasattr(self, '_initialized'):
            return
        
        self._batch_service = batch_service
        self._batch_repository = batch_repository
        self._max_concurrent_downloads = max_concurrent_downloads
        self._retry_attempts = retry_attempts
        self._retry_delay_seconds = retry_delay_seconds
        self._scan_interval_seconds = scan_interval_seconds
        
        # Processing management
        self._processing_batches: Set[PydanticObjectId] = set()
        self._retry_counts: Dict[PydanticObjectId, int] = {}
        
        # Service state
        self._is_running = False
        self._worker_tasks: List[asyncio.Task[None]] = []
        self._scanner_task: Optional[asyncio.Task[None]] = None
        self._shutdown_event = asyncio.Event()
        
        # Statistics and monitoring
        self._stats: Dict[str, Any] = {
            'total_discovered': 0,
            'total_processed': 0,
            'total_successful': 0,
            'total_failed': 0,
            'total_retried': 0,
            'current_processing': 0,
            'last_scan_time': None,
            'service_start_time': None,
        }
        
        self._initialized = True
        _log.info(
            f"BatchDownloadQueueService initialized with max_concurrent_downloads={max_concurrent_downloads}, "
            f"retry_attempts={retry_attempts}, scan_interval={scan_interval_seconds}s"
        )
    
    @classmethod
    async def get_instance(
        cls,
        batch_service: BatchService,
        batch_repository: BatchRepository,
        **kwargs: Any
    ) -> BatchDownloadQueueService:
        """
        Get or create the singleton instance with thread safety.
        
        Args:
            batch_service: Service for batch operations
            batch_repository: Repository for batch data access
            **kwargs: Additional configuration parameters
            
        Returns:
            The singleton instance
        """
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls(batch_service, batch_repository, **kwargs)
            return cls._instance
    
    async def start(self) -> None:
        """
        Start the service with scanner and worker tasks.
        
        This method is idempotent and can be called multiple times safely.
        """
        if self._is_running:
            _log.warning("BatchDownloadQueueService is already running")
            return
        
        self._is_running = True
        self._shutdown_event.clear()
        self._stats['service_start_time'] = datetime.now(timezone.utc).isoformat()
        
        # Start scanner task
        self._scanner_task = asyncio.create_task(
            self._batch_scanner(),
            name="batch_download_scanner"
        )
        
        # Start worker tasks
        for i in range(self._max_concurrent_downloads):
            task = asyncio.create_task(
                self._download_worker(worker_id=i),
                name=f"batch_download_worker_{i}"
            )
            self._worker_tasks.append(task)
        
        _log.info(
            f"BatchDownloadQueueService started with {self._max_concurrent_downloads} workers "
            f"and scanner interval of {self._scan_interval_seconds}s"
        )
    
    async def stop(self, timeout: float = 30.0) -> None:
        """
        Stop the service gracefully.
        
        Args:
            timeout: Maximum time to wait for tasks to finish
        """
        if not self._is_running:
            _log.info("BatchDownloadQueueService is not running")
            return
        
        _log.info("Stopping BatchDownloadQueueService...")
        
        # Signal shutdown
        self._is_running = False
        self._shutdown_event.set()
        
        # Cancel scanner task
        if self._scanner_task and not self._scanner_task.done():
            self._scanner_task.cancel()
        
        # Cancel worker tasks
        for task in self._worker_tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete or timeout
        tasks_to_wait = [self._scanner_task] + self._worker_tasks if self._scanner_task else self._worker_tasks
        if tasks_to_wait:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks_to_wait, return_exceptions=True),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                _log.warning("Some tasks did not complete within timeout")
        
        self._worker_tasks.clear()
        self._scanner_task = None
        _log.info("BatchDownloadQueueService stopped")
    
    async def _batch_scanner(self) -> None:
        """
        Scanner task that continuously looks for batches that need file collection.
        """
        _log.info("Batch scanner started")
        
        while self._is_running and not self._shutdown_event.is_set():
            try:
                await self._scan_and_queue_batches()
                
                # Wait before next scan
                await asyncio.sleep(self._scan_interval_seconds)
                
            except asyncio.CancelledError:
                _log.info("Batch scanner cancelled")
                break
            except Exception as e:
                _log.error(f"Batch scanner encountered error: {str(e)}")
                # Continue scanning on error
                await asyncio.sleep(self._scan_interval_seconds)
        
        _log.info("Batch scanner stopped")
    
    async def _scan_and_queue_batches(self) -> None:
        """
        Scan repository for batches that need file collection and queue them for processing.
        """
        try:
            # Find batches in terminal state with files not collected
            batches_to_process = await self._find_batches_needing_files()
            
            if not batches_to_process:
                _log.debug("No batches found needing file collection")
                return
            
            _log.info(f"Found {len(batches_to_process)} batches needing file collection")
            
            # Queue batches for processing (non-blocking)
            queued_count = 0
            for batch in batches_to_process:
                if await self._queue_batch_for_processing(batch):
                    queued_count += 1
            
            self._stats['total_discovered'] += len(batches_to_process)
            self._stats['last_scan_time'] = datetime.now(timezone.utc).isoformat()
            
            _log.info(f"Queued {queued_count} batches for processing")
            
        except Exception as e:
            _log.error(f"Error scanning for batches: {str(e)}")
    
    async def _find_batches_needing_files(self) -> List[Batch]:
        """
        Find batches that are in terminal state and need file collection.
        
        Returns:
            List of batches that need file collection
        """
        try:
            # Get batches in terminal state (completed, failed, etc.)
            batches = []
            async for batch in self._batch_repository.get_terminal_batches_no_files_iterator():
                if self._is_batch_eligible_for_download(batch):
                    batches.append(batch)
            
            return batches
            
        except Exception as e:
            _log.error(f"Error finding batches needing files: {str(e)}")
            return []
    
    def _is_batch_eligible_for_download(self, batch: Batch, force: bool = False) -> bool:
        """
        Check if a batch is eligible for file download.
        
        Args:
            batch: Batch entity to check
            force: Force eligibility check (for manual processing)
            
        Returns:
            True if batch is eligible for download
        """
        # Must be in terminal state
        if not batch.is_terminal_state:
            return False
        
        # Must not have files already collected
        if batch.files_collected:
            return False
        
        # Must have output or error files to download
        if not batch.output_file_id and not batch.error_file_id:
            return False
        
        # Must not already be processing
        if batch.id in self._processing_batches:
            return False
        
        return True
    
    async def _queue_batch_for_processing(self, batch: Batch) -> bool:
        """
        Queue a batch for processing by workers.
        
        Args:
            batch: Batch to queue
            
        Returns:
            True if batch was queued, False otherwise
        """
        # Check if we can process more batches
        if len(self._processing_batches) >= self._max_concurrent_downloads:
            _log.debug(f"At capacity ({self._max_concurrent_downloads}), cannot queue batch {batch.id}")
            return False
        
        # Mark as processing immediately to prevent duplicate processing
        self._processing_batches.add(batch.id)
        self._stats['current_processing'] = len(self._processing_batches)
        
        _log.debug(f"Queued batch {batch.id} for processing")
        return True
    
    async def _download_worker(self, worker_id: int) -> None:
        """
        Worker coroutine that processes batches from the processing set.
        
        Args:
            worker_id: Unique identifier for this worker
        """
        _log.info(f"Download worker {worker_id} started")
        
        while self._is_running and not self._shutdown_event.is_set():
            try:
                # Find a batch to process
                batch_to_process = await self._get_next_batch_to_process(worker_id)
                if not batch_to_process:
                    # No batches available, wait before checking again
                    await asyncio.sleep(1.0)
                    continue
                
                # Process the batch
                await self._process_batch_download(batch_to_process, worker_id)
                
            except asyncio.CancelledError:
                _log.info(f"Download worker {worker_id} cancelled")
                break
            except Exception as e:
                _log.error(f"Download worker {worker_id} encountered error: {str(e)}")
                # Continue processing other batches
                continue
        
        _log.info(f"Download worker {worker_id} stopped")
    
    async def _get_next_batch_to_process(self, worker_id: int) -> Optional[Batch]:
        """
        Get the next batch to process from the processing set.
        
        Args:
            worker_id: ID of the worker requesting a batch
            
        Returns:
            Batch to process, or None if none available
        """
        # Find a batch that's marked as processing but not yet started
        for batch_id in list(self._processing_batches):
            try:
                # Get fresh batch data from repository
                batch = await self._batch_repository.retrieve(batch_id)
                
                # Check if still eligible
                if self._is_batch_eligible_for_download(batch):
                    return batch
                else:
                    # No longer eligible, remove from processing
                    self._processing_batches.discard(batch_id)
                    self._stats['current_processing'] = len(self._processing_batches)
                    
            except Exception as e:
                _log.error(f"Error getting batch {batch_id}: {str(e)}")
                # Remove problematic batch from processing
                self._processing_batches.discard(batch_id)
                self._stats['current_processing'] = len(self._processing_batches)
        
        return None
    
    async def _process_batch_download(self, batch: Batch, worker_id: int) -> None:
        """
        Process a single batch download with retry logic.
        
        Args:
            batch: Batch to process
            worker_id: ID of the worker processing this batch
        """
        batch_id = batch.id
        
        _log.info(f"Worker {worker_id} starting download for batch {batch_id}")
        
        start_time = time.time()
        success = False
        
        try:
            # Attempt download with retries
            for attempt in range(self._retry_attempts + 1):
                try:
                    # Call the batch service to download and store files
                    download_response = await self._batch_service.download_and_store_batch_files(batch)
                    
                    _log.info(
                        f"Worker {worker_id} successfully downloaded files for batch {batch_id}: "
                        f"output={download_response.output_file_name}, "
                        f"error={download_response.error_file_name}"
                    )
                    
                    success = True
                    break
                    
                except Exception as e:
                    _log.error(
                        f"Worker {worker_id} failed to download batch {batch_id} "
                        f"(attempt {attempt + 1}/{self._retry_attempts + 1}): {str(e)}"
                    )
                    
                    # If this isn't the last attempt, wait before retrying
                    if attempt < self._retry_attempts:
                        self._stats['total_retried'] += 1
                        await asyncio.sleep(self._retry_delay_seconds * (attempt + 1))  # Exponential backoff
                    else:
                        # Final attempt failed
                        break
            
            # Update statistics
            execution_time = time.time() - start_time
            self._stats['total_processed'] += 1
            
            if success:
                self._stats['total_successful'] += 1
                _log.info(
                    f"Worker {worker_id} completed batch {batch_id} successfully "
                    f"in {execution_time:.2f}s"
                )
            else:
                self._stats['total_failed'] += 1
                _log.error(
                    f"Worker {worker_id} failed to process batch {batch_id} "
                    f"after {self._retry_attempts + 1} attempts in {execution_time:.2f}s"
                )
            
        finally:
            # Remove from processing set
            self._processing_batches.discard(batch_id)
            self._retry_counts.pop(batch_id, None)
            self._stats['current_processing'] = len(self._processing_batches)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current service status for monitoring.
        
        Returns:
            Dictionary containing service status information
        """
        return {
            'service_status': 'running' if self._is_running else 'stopped',
            'processing_count': len(self._processing_batches),
            'processing_batches': list(str(batch_id) for batch_id in self._processing_batches),
            'worker_count': len(self._worker_tasks),
            'active_workers': sum(1 for task in self._worker_tasks if not task.done()),
            'scanner_running': self._scanner_task is not None and not self._scanner_task.done(),
            'configuration': {
                'max_concurrent_downloads': self._max_concurrent_downloads,
                'retry_attempts': self._retry_attempts,
                'retry_delay_seconds': self._retry_delay_seconds,
                'scan_interval_seconds': self._scan_interval_seconds,
            },
            'statistics': self._stats.copy(),
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status for monitoring and alerting.
        
        Returns:
            Dictionary containing health information
        """
        health_status = "healthy"
        issues = []
        
        # Check if service is running
        if not self._is_running:
            health_status = "critical"
            issues.append("Service is not running")
        
        # Check scanner task
        if not self._scanner_task or self._scanner_task.done():
            health_status = "critical"
            issues.append("Batch scanner is not running")
        
        # Check worker tasks
        dead_workers = sum(1 for task in self._worker_tasks if task.done())
        if dead_workers > 0:
            health_status = "warning" if dead_workers < len(self._worker_tasks) else "critical"
            issues.append(f"{dead_workers} worker tasks have stopped")
        
        # Check for stuck processing
        if len(self._processing_batches) >= self._max_concurrent_downloads:
            health_status = "warning"
            issues.append("All workers appear to be busy")
        
        return {
            'health_status': health_status,
            'issues': issues,
            'service_running': self._is_running,
            'scanner_status': {
                'running': self._scanner_task is not None and not self._scanner_task.done(),
                'scan_interval_seconds': self._scan_interval_seconds,
            },
            'worker_status': {
                'total_workers': len(self._worker_tasks),
                'active_workers': len(self._worker_tasks) - dead_workers,
                'dead_workers': dead_workers,
            },
            'processing_metrics': {
                'processing_count': len(self._processing_batches),
                'max_concurrent': self._max_concurrent_downloads,
            },
            'uptime': self._get_uptime_seconds(),
        }
    
    def _get_uptime_seconds(self) -> Optional[float]:
        """
        Get service uptime in seconds.
        
        Returns:
            Uptime in seconds, or None if not started
        """
        if not self._stats['service_start_time']:
            return None
        
        start_time_str = self._stats['service_start_time']
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            return (current_time - start_time).total_seconds()
        return None
    
    async def wait_for_processing_complete(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all processing to complete.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if processing is complete, False if timeout occurred
        """
        try:
            # Wait for all processing to complete
            while self._processing_batches and self._is_running:
                await asyncio.sleep(0.1)
            
            return True
            
        except asyncio.TimeoutError:
            return False
    
    @property
    def is_running(self) -> bool:
        """Check if the service is currently running."""
        return self._is_running
    
    @property
    def processing_count(self) -> int:
        """Get number of batches currently being processed."""
        return len(self._processing_batches)
