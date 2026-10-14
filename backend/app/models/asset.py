"""Asset model for infrastructure assets."""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator

class Asset(SQLModel, table=True):
    """
    Infrastructure asset model.
    
    Represents physical infrastructure assets like streetlights, roads, etc.
    """
    
    __tablename__ = "assets"
    
    # Primary key
    id: str = Field(primary_key=True, description="Unique asset identifier (e.g., SL-W12-001)")
    
    # Asset details
    asset_type: str = Field(
        description="Type of asset (Streetlight, Road & pavement, Drainage, Public space, Electrical)"
    )
    name: str = Field(description="Human-readable asset name")
    ward: str = Field(description="Ward where asset is located")
    
    # Geolocation
    latitude: Optional[float] = Field(
        None, 
        ge=-90, 
        le=90,
        description="Latitude coordinate (optional, -90 to 90)"
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Longitude coordinate (optional, -180 to 180)"
    )
    
    # Asset lifecycle
    installation_date: Optional[datetime] = Field(None, description="Installation date")
    condition: str = Field(
        default="Unknown",
        description="Asset condition (Good, Fair, Poor, Critical)"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    complaints: List["Complaint"] = Relationship(back_populates="asset")
    
    @field_validator("latitude", "longitude", mode="before")
    @classmethod
    def validate_coordinates(cls, v):
        """Validate latitude and longitude ranges."""
        if v is not None:
            # Latitude: -90 to 90
            if isinstance(v, (int, float)):
                if not (-90 <= v <= 90):
                    raise ValueError("Latitude must be between -90 and 90")
            # Longitude: -180 to 180
        return v
