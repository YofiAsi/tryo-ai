from dataclasses import dataclass
from openai.types.file_object import FileObject as OpenAiFileDTO
from openai.types.batch import Batch as OpenAiBatchDTO

@dataclass
class BatchOperationResponse:
    file_operation_response: OpenAiFileDTO
    batch_operation_response: OpenAiBatchDTO