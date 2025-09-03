from pathlib import Path
from typing import Union

from temporalio import activity


@activity.defn
def pre_process_files(root_folder_path: Union[str, Path]) -> str:
    """Pre-process files in the given root folder path."""
    # TODO: Implement file preprocessing logic
    return str(root_folder_path)