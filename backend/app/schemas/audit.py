"""Audit log API schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AuditLogSchema(BaseModel):
    """Audit log entry schema."""
    
    id: Optional[int]
    complaint_id: Optional[str]
    repair_id: Optional[str]
    action: str = Field(description="Action type")
    actor: Optional[str]
    source: str = Field(description="Source of action")
    old_value: Optional[str]
    new_value: Optional[str]
    details: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True
