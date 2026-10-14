"""Priority evaluation schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class PriorityEvaluationSchema(BaseModel):
    """Response schema for priority evaluation endpoints."""
    
    complaint_id: str = Field(description="Complaint ID")
    priority_category: str = Field(description="Priority level (Low, Medium, High, Critical)")
    priority_score: Optional[int] = Field(None, description="Numeric score 0-100 if provided by engine", ge=0, le=100)
    explanation: str = Field(description="Human-readable explanation of priority")
    contributing_factors: Optional[Dict[str, Any]] = Field(None, description="Factors influencing the score")
    model_version: str = Field(description="Priority engine version (e.g., 'development-mock-v1')")
    evaluated_at: datetime = Field(description="When evaluation was performed")
    
    class Config:
        from_attributes = True


class PrioritySummarySchema(BaseModel):
    """Summary of complaints grouped by priority."""
    
    total_complaints: int = Field(description="Total number of complaints")
    by_priority: Dict[str, int] = Field(description="Count of complaints by priority level")
    distribution_percentage: Dict[str, float] = Field(description="Percentage distribution")
    
    class Config:
        from_attributes = True
