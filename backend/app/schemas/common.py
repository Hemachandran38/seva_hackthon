"""Common schemas used across the API."""

from typing import Generic, TypeVar, List, Any, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    
    items: List[T]
    total: int = Field(description="Total number of items")
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Number of items returned")
    
    @property
    def page(self) -> int:
        """Calculate current page number."""
        return (self.skip // self.limit) + 1 if self.limit > 0 else 1


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    detail: str = Field(description="Error message")
    status_code: int = Field(description="HTTP status code")
    timestamp: Optional[str] = Field(None, description="When error occurred")
