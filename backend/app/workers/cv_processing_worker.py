import logging
import uuid
from typing import List
from datetime import datetime, timezone

from celery import current_task
from app.conf.celery_config import celery_app
from app.entity.task_entity import Task, TaskStatus, TaskType
from app.schema.tasks_dto import CVProcessingTaskDTO
from app.repository.task_repository import TaskRepository
from app.errors.business_exception import BusinessException, ErrorCodes

_log = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.workers.cv_processing_worker.process_cv_processing")
def process_cv_processing(self, task_id: str, candidates_ids: List[str]):
    """
    Process CV processing task for multiple candidates
    
    Args:
        task_id: The task ID to track progress
        candidates_ids: List of candidate IDs to process
    """
    _log.info(f"Starting CV processing task {task_id} for {len(candidates_ids)} candidates")
    
    try:
        # Update task status to processing
        task_repo = TaskRepository()
        
        # Convert string task_id to UUID
        task_uuid = uuid.UUID(task_id)
        
        # Retrieve the task
        task = task_repo.retrieve_sync(task_uuid)
        if not task:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Task not found: {task_id}")
        
        # Update status to processing
        task.status = TaskStatus.PROCESSING
        task.progress_percentage = 0.0
        task.updated_at = datetime.now(timezone.utc)
        task_repo.update_sync(task)
        
        total_candidates = len(candidates_ids)
        processed_count = 0
        
        # Process each candidate
        for i, candidate_id in enumerate(candidates_ids):
            try:
                # Simulate CV processing work
                _log.info(f"Processing candidate {candidate_id} ({i+1}/{total_candidates})")
                
                # Update progress
                progress = ((i + 1) / total_candidates) * 100
                task.progress_percentage = progress
                task.updated_at = datetime.now(timezone.utc)
                task_repo.update_sync(task)
                
                # Simulate processing time (replace with actual CV processing logic)
                import time
                time.sleep(2)  # Simulate 2 seconds of processing
                
                processed_count += 1
                
                # Update Celery task state
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i + 1,
                        "total": total_candidates,
                        "status": f"Processed {i + 1}/{total_candidates} candidates"
                    }
                )
                
            except Exception as e:
                _log.error(f"Error processing candidate {candidate_id}: {str(e)}")
                # Continue with other candidates even if one fails
        
        # Update task status to completed
        task.status = TaskStatus.COMPLETED
        task.progress_percentage = 100.0
        task.updated_at = datetime.now(timezone.utc)
        task_repo.update_sync(task)
        
        _log.info(f"CV processing task {task_id} completed successfully. Processed {processed_count}/{total_candidates} candidates")
        
        return {
            "status": "completed",
            "task_id": task_id,
            "processed_count": processed_count,
            "total_count": total_candidates,
            "message": f"Successfully processed {processed_count}/{total_candidates} candidates"
        }
        
    except Exception as e:
        _log.error(f"CV processing task {task_id} failed: {str(e)}")
        
        # Update task status to failed
        try:
            task_repo = TaskRepository()
            task_uuid = uuid.UUID(task_id)
            task = task_repo.retrieve_sync(task_uuid)
            if task:
                task.status = TaskStatus.FAILED
                task.updated_at = datetime.now(timezone.utc)
                task_repo.update_sync(task)
        except Exception as update_error:
            _log.error(f"Failed to update task status to failed: {str(update_error)}")
        
        # Re-raise the exception to mark Celery task as failed
        raise


@celery_app.task(bind=True, name="app.workers.cv_processing_worker.simple_cv_processing")
def simple_cv_processing(self, task_id: str, candidates_ids: List[str]):
    """
    Simple CV processing task for testing purposes
    """
    _log.info(f"Simple CV processing task {task_id} started")
    
    try:
        # Simulate some processing time
        import time
        time.sleep(5)
        
        _log.info(f"Simple CV processing task {task_id} completed")
        
        return {
            "status": "completed",
            "task_id": task_id,
            "message": "Simple CV processing completed successfully"
        }
        
    except Exception as e:
        _log.error(f"Simple CV processing task {task_id} failed: {str(e)}")
        raise
