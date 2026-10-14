"""Repair record models for tracking repairs and maintenance."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator

class RepairRecord(SQLModel, table=True):
    """
    Repair record model.
    
    Tracks repairs and maintenance work related to complaints.
    """
    
    __tablename__ = "repair_records"
    
    # Primary key
    id: str = Field(primary_key=True, description="Unique repair record ID")
    
    # Relationship
    complaint_id: str = Field(foreign_key="complaints.id")
    
    # Repair details
    assigned_team: Optional[str] = Field(None, description="Team assigned to repair")
    description: str = Field(description="Description of repair work performed")
    repair_date: Optional[datetime] = Field(None, description="Date when repair was completed")
    
    # Verification
    verification_status: str = Field(
        default="Pending",
        description="Verification status (Pending, Verified, Failed, Rejected)"
    )
    evidence_reference: Optional[str] = Field(None, description="Reference to verification evidence (photo URL, etc)")
    
    # Verification details (only set when actually verified)
    verified_at: Optional[datetime] = Field(None, description="Timestamp of verification")
    verified_by: Optional[str] = Field(None, description="Person/system that verified the repair")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    complaint: Optional["Complaint"] = Relationship(back_populates="repair_records")
    
    @field_validator("verification_status")
    @classmethod
    def validate_verification_status(cls, v):
        """Validate verification status."""
        allowed = {"Pending", "Verified", "Failed", "Rejected"}
        if v not in allowed:
            raise ValueError(f"Verification status must be one of {allowed}")
        return v
