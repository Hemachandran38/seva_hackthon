"""Audit log model for tracking system actions."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class AuditLog(SQLModel, table=True):
    """
    Audit log model.
    
    Tracks all significant actions for accountability and debugging.
    Append-only: created through API, never edited or deleted.
    """
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id: Optional[int] = Field(primary_key=True)
    
    # Related entity
    complaint_id: Optional[str] = Field(None, foreign_key="complaints.id")
    repair_id: Optional[str] = Field(None, description="Repair record ID if action is repair-related")
    
    # Action details
    action: str = Field(
        description="Action type: 'create', 'status_change', 'assignment', 'repair_start', 'repair_complete', 'verification', 'verification_failed', 'update', etc"
    )
    actor: Optional[str] = Field(None, description="User or system that performed action (defaults to 'system' if not provided)")
    source: str = Field(default="api", description="Source of action (api, web, migration, system)")
    
    # Old and new values for tracking changes
    old_value: Optional[str] = Field(None, description="Previous value (for updates)")
    new_value: Optional[str] = Field(None, description="New value (for updates)")
    
    # Details
    details: Optional[str] = Field(None, description="Additional context about action")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    complaint: Optional["Complaint"] = Relationship(back_populates="audit_logs")
