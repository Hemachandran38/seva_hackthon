"""Complaint models for infrastructure issue reporting."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator

# Valid status transitions: defines which statuses can follow which
VALID_STATUS_TRANSITIONS = {
    "Reported": {"Under Review", "Assigned"},
    "Under Review": {"Assigned", "Reported"},
    "Assigned": {"In Progress", "Under Review"},
    "In Progress": {"Awaiting Verification", "Assigned"},
    "Awaiting Verification": {"Resolved", "In Progress"},
    "Resolved": {"Under Review"},  # Re-open if needed
}

class ComplaintTimeline(SQLModel, table=True):
    """Timeline entry for complaint status changes."""
    
    __tablename__ = "complaint_timeline"
    
    id: Optional[int] = Field(primary_key=True)
    complaint_id: str = Field(foreign_key="complaints.id")
    status: str = Field(description="Status at this point in timeline")
    note: str = Field(description="Note or comment for this status change")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    complaint: Optional["Complaint"] = Relationship(back_populates="timeline_entries")


class Complaint(SQLModel, table=True):
    """
    Complaint model for infrastructure issues.
    
    Represents citizen reports of infrastructure problems.
    """
    
    __tablename__ = "complaints"
    
    # Primary key
    id: str = Field(primary_key=True, description="Unique complaint ID (e.g., CP-2026-0101)")
    
    # Issue details
    title: str = Field(description="Short title of the issue")
    description: str = Field(description="Detailed problem description")
    category: str = Field(
        description="Issue category (Streetlight, Road & pavement, Drainage, Public space, Electrical Hazard)"
    )
    
    # Location
    location_text: str = Field(description="Human-readable location description")
    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Latitude coordinate (optional, unverified location)"
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Longitude coordinate (optional, unverified location)"
    )
    ward: Optional[str] = Field(None, description="Ward number or identifier")
    
    # Priority and status
    priority: str = Field(
        default="Medium",
        description="Priority level (Low, Medium, High, Critical)"
    )
    priority_score: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Priority score from 0-100"
    )
    status: str = Field(
        default="Reported",
        description="Current status (Reported, Under Review, Assigned, In Progress, Awaiting Verification, Resolved)"
    )
    
    # Recurrence tracking
    repeat_complaint_count: int = Field(
        default=0,
        ge=0,
        description="Number of times this issue has been reported"
    )
    
    # Asset relationship
    asset_id: Optional[str] = Field(None, foreign_key="assets.id")
    
    # Assignment
    assigned_team: Optional[str] = Field(None, description="Name of team handling this complaint")
    
    # Media
    image_reference: Optional[str] = Field(None, description="Reference to uploaded image or photo")
    
    # Timestamps
    reported_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    asset: Optional["Asset"] = Relationship(back_populates="complaints")
    timeline_entries: List[ComplaintTimeline] = Relationship(back_populates="complaint")
    repair_records: List["RepairRecord"] = Relationship(back_populates="complaint")
    audit_logs: List["AuditLog"] = Relationship(back_populates="complaint")
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        """Validate priority is one of allowed values."""
        allowed = {"Low", "Medium", "High", "Critical"}
        if v not in allowed:
            raise ValueError(f"Priority must be one of {allowed}")
        return v
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate status is one of allowed values."""
        allowed = {"Reported", "Under Review", "Assigned", "In Progress", "Awaiting Verification", "Resolved"}
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v
    
    @field_validator("priority_score")
    @classmethod
    def validate_score(cls, v):
        """Validate priority score is 0-100."""
        if not (0 <= v <= 100):
            raise ValueError("Priority score must be between 0 and 100")
        return v
    
    @field_validator("latitude", "longitude", mode="before")
    @classmethod
    def validate_coordinates(cls, v):
        """Validate latitude and longitude ranges."""
        if v is not None and isinstance(v, (int, float)):
            if not (-90 <= v <= 90 if v is cls.latitude else -180 <= v <= 180):
                raise ValueError("Invalid coordinate range")
        return v
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check if transition from current status to new_status is valid."""
        return new_status in VALID_STATUS_TRANSITIONS.get(self.status, set())
