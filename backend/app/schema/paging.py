
import json
from typing import Dict, Any

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator


class PagingDTO(BaseModel):
    """
    Query parameters for list and filter operations.

    Parameters:
    -----------
    page: int
        Offset for the page.

    size: int
        Limit for the page.

    Returns:
    --------
    dict:
        Query parameters.
    """

    page: int = 1
    size: int = 10