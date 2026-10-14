"""Repair record API schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class RepairRecordCreateSchema(BaseModel):
    """Schema for creating a repair record."""
    
    complaint_id: str = Field(description="Related complaint ID")
    assigned_team: Optional[str] = None
    description: str = Field(min_length=10, description="Description of repair work")
    repair_date: Optional[datetime] = None


class RepairRecordProgressSchema(BaseModel):
    """Schema for updating repair progress."""
    
    repair_date: Optional[datetime] = Field(None, description="When repair was completed")
    description: Optional[str] = Field(None, min_length=10, description="Updated work description")


class RepairRecordVerifySchema(BaseModel):
    """Schema for verifying/completing a repair."""
    
    verification_status: str = Field(description="Verification status (Verified, Failed, Rejected)")
    evidence_reference: Optional[str] = Field(None, description="Reference to verification evidence (photo URL, etc)")
    verified_by: Optional[str] = Field(None, description="Person/system verifying the repair")


class RepairRecordSchema(BaseModel):
    """Full repair record schema for responses."""
    
    id: str
    complaint_id: str
    assigned_team: Optional[str]
    description: str
    repair_date: Optional[datetime]
    verification_status: str
    evidence_reference: Optional[str]
    verified_at: Optional[datetime]
    verified_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
