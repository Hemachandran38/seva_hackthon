"""Complaint API schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class ComplaintTimelineSchema(BaseModel):
    """Timeline entry schema."""
    
    status: str = Field(description="Status at this point")
    note: str = Field(description="Note about status change")
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AuditLogSchema(BaseModel):
    """Audit log entry schema."""
    
    id: Optional[int]
    action: str = Field(description="Action type")
    actor: Optional[str]
    source: str = Field(description="Source of action")
    old_value: Optional[str]
    new_value: Optional[str]
    details: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ComplaintCreateSchema(BaseModel):
    """Schema for creating a new complaint."""
    
    title: str = Field(min_length=1, max_length=255, description="Issue title")
    description: str = Field(min_length=10, description="Issue description")
    category: str = Field(description="Issue category")
    location_text: str = Field(description="Location description")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    ward: Optional[str] = None
    asset_id: Optional[str] = None
    image_reference: Optional[str] = None


class ComplaintPatchSchema(BaseModel):
    """Schema for updating complaint fields (PATCH)."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    priority: Optional[str] = None
    priority_score: Optional[int] = Field(None, ge=0, le=100)
    assigned_team: Optional[str] = None
    repeat_complaint_count: Optional[int] = Field(None, ge=0)


class ComplaintStatusUpdateSchema(BaseModel):
    """Schema for updating complaint status with validation."""
    
    status: str = Field(description="New status")
    note: Optional[str] = Field(None, description="Optional note for timeline")


class ComplaintUpdateSchema(BaseModel):
    """Schema for updating a complaint (deprecated, use PATCH instead)."""
    
    status: Optional[str] = None
    priority: Optional[str] = None
    priority_score: Optional[int] = Field(None, ge=0, le=100)
    assigned_team: Optional[str] = None
    repeat_complaint_count: Optional[int] = None


class ComplaintSchema(BaseModel):
    """Full complaint schema for responses."""
    
    id: str
    title: str
    description: str
    category: str
    location_text: str
    latitude: Optional[float]
    longitude: Optional[float]
    ward: Optional[str]
    priority: str
    priority_score: int
    status: str
    repeat_complaint_count: int
    asset_id: Optional[str]
    assigned_team: Optional[str]
    image_reference: Optional[str]
    reported_at: datetime
    updated_at: datetime
    timeline_entries: List[ComplaintTimelineSchema] = []
    
    class Config:
        from_attributes = True
