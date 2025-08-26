"""
PageResponse class for paginated API responses
"""
from typing import List, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')


class PageResponse(BaseModel, Generic[T]):
    """
    Generic paginated response model
    
    Used for returning paginated results from repository queries
    """
    content: List[T]
    page: int
    size: int
    total: int
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages"""
        if self.size <= 0:
            return 0
        return (self.total + self.size - 1) // self.size
    
    @property
    def has_next(self) -> bool:
        """Check if there are more pages"""
        return self.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there are previous pages"""
        return self.page > 1
    
    class Config:
        arbitrary_types_allowed = True
