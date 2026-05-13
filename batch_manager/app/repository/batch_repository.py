from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, AsyncIterator, List, Optional

from app.conf.page_response import PageResponse
from app.entity.batch_entity import Batch, BatchStatus
from app.errors.business_exception import BusinessException, ErrorCodes

if TYPE_CHECKING:
    from datetime import datetime

    from beanie import PydanticObjectId

_log = logging.getLogger(__name__)


class BatchRepository:
    """
    Batch Repository class

    This class is responsible for handling all the database operations related to the Batch entity.
    Batch entity is a beanie document model and all the operations are performed using the beanie library.
    """

    def __init__(self) -> None:
        _log.debug("BatchRepository Connecting to database")

    async def create(self, batch: Batch) -> Batch:
        _log.debug(f"BatchRepository Creating batch: {batch.id}")
        await Batch.insert(batch)
        _log.debug("BatchRepository Batch created")
        return batch

    async def bulk_create(self, batches: List[Batch]) -> List[Batch]:
        """
        Create multiple batches in a single database operation.
        
        Args:
            batches: List of Batch entities to create
            
        Returns:
            List of created Batch entities with assigned IDs
            
        Raises:
            BusinessException: If bulk creation fails
        """
        if not batches:
            _log.warning("BatchRepository No batches to create")
            return []
        
        _log.debug(f"BatchRepository Creating {len(batches)} batches in bulk")
        
        try:
            # Use Beanie's insert_many for bulk insertion
            await Batch.insert_many(batches)
            _log.info(f"BatchRepository Successfully created {len(batches)} batches")
            return batches
        except Exception as e:
            _log.error(f"BatchRepository Failed to bulk create batches: {str(e)}")
            raise BusinessException(ErrorCodes.INTERNAL_SERVER_ERROR, f"Failed to create batches: {str(e)}")

    async def update(self, batch: Batch) -> Batch:
        _log.debug(f"BatchRepository Updating batch: {batch.id}")
        if batch.id is None:
            raise BusinessException(ErrorCodes.INVALID_PAYLOAD, "Batch id is required for update")
        await batch.replace()
        _log.debug("BatchRepository Batch updated")
        return batch

    async def delete(self, id: PydanticObjectId) -> None:
        _log.debug(f"BatchRepository Deleting batch: {id}")
        result = await Batch.find_one({"_id": id})
        if not result:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Batch not found: {id}")

        await result.delete()
        _log.debug("BatchRepository Batch deleted")

    async def find(self, query: str | None = None, page: int = 1, size: int = 10, sort: str = "-created_at") -> PageResponse[Batch]:
        _log.debug("BatchRepository list request")
        if query is None:
            query_dict = {}
        else:
            query_dict = json.loads(query)

        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Batch.find(query_dict).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Batch.find(query_dict).skip((page-1) * size).limit(size).sort(sort)
        content = await document.to_list()
        _log.debug("BatchRepository Batches retrieved")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def count(self, query_dict: dict[str, Any]) -> int:
        _log.debug(f"BatchRepository Counting batches with query: {query_dict}")
        doc = Batch.find(query_dict)
        result = await doc.count()
        _log.debug("BatchRepository Batches counted")
        return result

    async def retrieve(self, id: PydanticObjectId) -> Batch:
        _log.debug(f"BatchRepository Retrieving batch: {id}")
        doc = await Batch.find_one({"_id": id})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Batch not found: {id}")
        _log.debug("BatchRepository Batch retrieved")
        return doc

    async def retrieve_by_batch_id(self, batch_id: PydanticObjectId) -> Batch:
        _log.debug(f"BatchRepository Retrieving batch by batch_id: {batch_id}")
        doc = await Batch.find_one({"_id": batch_id})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"Batch not found: {batch_id}")
        _log.debug("BatchRepository Batch retrieved")
        return doc

    async def retrieve_by_openai_batch_id(self, openai_batch_id: str) -> Optional[Batch]:
        _log.debug(f"BatchRepository Retrieving batch by openai_batch_id: {openai_batch_id}")
        doc = await Batch.find_one({"openai_batch_id": openai_batch_id})
        _log.debug("BatchRepository Batch retrieved by OpenAI ID")
        return doc

    async def find_by_status(self, status: BatchStatus, page: int = 1, size: int = 10) -> PageResponse[Batch]:
        _log.debug(f"BatchRepository Finding batches by status: {status}")
        query = {"status": status.value}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Batch.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Batch.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("BatchRepository Batches found by status")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_by_task_id(self, task_id: PydanticObjectId, page: int = 1, size: int = 10) -> PageResponse[Batch]:
        _log.debug(f"BatchRepository Finding batches by task_id: {task_id}")
        query = {"task_id": task_id}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Batch.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Batch.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("BatchRepository Batches found by task_id")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_by_api_key_id(self, api_key_id: str, page: int = 1, size: int = 10) -> PageResponse[Batch]:
        _log.debug(f"BatchRepository Finding batches by api_key_id: {api_key_id}")
        query = {"api_key_id": api_key_id}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Batch.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Batch.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("BatchRepository Batches found by api_key_id")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_in_progress_batches(self, page: int = 1, size: int = 10) -> PageResponse[Batch]:
        _log.debug("BatchRepository Finding in-progress batches")
        query = {"status": {"$in": [
            BatchStatus.VALIDATING.value,
            BatchStatus.IN_PROGRESS.value,
            BatchStatus.FINALIZING.value
        ]}}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Batch.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Batch.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("BatchRepository In-progress batches found")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_terminal_batches(self, page: int = 1, size: int = 10) -> PageResponse[Batch]:
        _log.debug("BatchRepository Finding terminal batches")
        query = {"status": {"$in": [
            BatchStatus.COMPLETED.value,
            BatchStatus.FAILED.value,
            BatchStatus.EXPIRED.value,
            BatchStatus.CANCELLED.value
        ]}}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Batch.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Batch.find(query).skip((page-1) * size).limit(size).sort("-completed_at")
        content = await document.to_list()
        _log.debug("BatchRepository Terminal batches found")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def count_by_status(self, status: BatchStatus) -> int:
        _log.debug(f"BatchRepository Counting batches by status: {status}")
        query = {"status": status.value}
        result = await Batch.find(query).count()
        _log.debug("BatchRepository Batches counted by status")
        return result

    async def count_by_task_id(self, task_id: PydanticObjectId) -> int:
        _log.debug(f"BatchRepository Counting batches by task_id: {task_id}")
        query = {"task_id": task_id}
        result = await Batch.find(query).count()
        _log.debug("BatchRepository Batches counted by task_id")
        return result

    async def find_batches_created_after(self, after_date: datetime, page: int = 1, size: int = 10) -> PageResponse[Batch]:
        _log.debug(f"BatchRepository Finding batches created after: {after_date}")
        query = {"created_at": {"$gte": after_date}}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Batch.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Batch.find(query).skip((page-1) * size).limit(size).sort("-created_at")
        content = await document.to_list()
        _log.debug("BatchRepository Batches found by creation date")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def find_batches_with_errors(self, page: int = 1, size: int = 10) -> PageResponse[Batch]:
        _log.debug("BatchRepository Finding batches with errors")
        query = {"errors": {"$ne": None}}
        
        if page < 1:
            raise BusinessException(ErrorCodes.INVALID_INPUT, "Invalid page idx")

        total_count = await Batch.find(query).count()
        if total_count == 0:
            return PageResponse(content=[], page=page, size=size, total=total_count)

        document = Batch.find(query).skip((page-1) * size).limit(size).sort("-failed_at")
        content = await document.to_list()
        _log.debug("BatchRepository Batches with errors found")
        return PageResponse(content=content, page=page, size=size, total=total_count)

    async def get_pending_batches_iterator(self) -> AsyncIterator[Batch]:
        """
        Get pending batches iterator.
        """
        cursor = Batch.find({"status": BatchStatus.PENDING_UPLOAD.value}).sort("-created_at")
        async for batch in cursor:
            yield batch
    
    async def get_non_terminal_state_batches_iterator(self) -> AsyncIterator[Batch]:
        """
        Get non terminal state batches iterator.
        """
        cursor = Batch.find({"status": {"$nin": [
            BatchStatus.TERMINAL_STATES.value
        ]}}).sort("-created_at")
        async for batch in cursor:
            yield batch
    
    async def get_terminal_state_batches_iterator(self) -> AsyncIterator[Batch]:
        """
        Get terminal state batches iterator.
        """
        cursor = Batch.find({"status": {"$in": [
            BatchStatus.TERMINAL_STATES.value
        ]}}).sort("-completed_at")
        async for batch in cursor:
            yield batch

    async def get_terminal_batches_no_files_iterator(self) -> AsyncIterator[Batch]:
        """
        Get terminal state batches iterator that do not have files collected.
        """
        cursor = Batch.find({
            Batch.status: {
                "$in": [
                    BatchStatus.TERMINAL_STATES.value
                ]},
            Batch.files_collected: {
                "$eq": False
            }
        }).sort("-completed_at")
        
        async for batch in cursor:
            yield batch
