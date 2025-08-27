"""Service for managing OpenAI API operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openai.types.batch import Batch as OpenAiBatchDTO
    from openai.types.file_object import FileObject as OpenAiFileDTO


@dataclass
class BatchOperationResponse:
    file_operation_response: OpenAiFileDTO
    batch_operation_response: OpenAiBatchDTO