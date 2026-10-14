"""Asset API schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class AssetCreateSchema(BaseModel):
    """Schema for creating a new asset."""
    
    id: str = Field(description="Unique asset ID (e.g., SL-W12-001)")
    asset_type: str = Field(description="Type of asset")
    name: str = Field(description="Asset name")
    ward: str = Field(description="Ward identifier")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    installation_date: Optional[datetime] = None
    condition: str = Field(default="Unknown")


class AssetUpdateSchema(BaseModel):
    """Schema for updating an asset."""
    
    name: Optional[str] = None
    condition: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class AssetSchema(BaseModel):
    """Full asset schema for responses."""
    
    id: str
    asset_type: str
    name: str
    ward: str
    latitude: Optional[float]
    longitude: Optional[float]
    installation_date: Optional[datetime]
    condition: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
