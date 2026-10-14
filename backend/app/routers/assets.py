"""Asset management endpoints."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, desc
from app.database import get_session
from app.models.asset import Asset
from app.schemas.asset import AssetSchema, AssetCreateSchema, AssetUpdateSchema
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/api/assets", tags=["assets"])

@router.get("", response_model=PaginatedResponse[AssetSchema])
async def list_assets(
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    ward: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
):
    """
    List all assets with optional filtering and pagination.
    
    **Filters:**
    - **ward**: Filter by ward identifier
    - **asset_type**: Filter by asset type (Streetlight, Road & pavement, Drainage, etc)
    
    **Pagination:**
    - **skip**: Number of items to skip (default: 0)
    - **limit**: Number of items to return (1-100, default: 10)
    """
    query = select(Asset)
    
    if ward:
        query = query.where(Asset.ward == ward)
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
    
    # Get total count
    total_query = select(Asset)
    if ward:
        total_query = total_query.where(Asset.ward == ward)
    if asset_type:
        total_query = total_query.where(Asset.asset_type == asset_type)
    
    total = len(session.exec(total_query).all())
    
    # Get paginated results, ordered by most recent first
    assets = session.exec(query.order_by(desc(Asset.created_at)).offset(skip).limit(limit)).all()
    
    return PaginatedResponse(
        items=assets,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{asset_id}", response_model=AssetSchema)
async def get_asset(asset_id: str, session: Session = Depends(get_session)):
    """Get a specific asset by ID."""
    asset = session.exec(select(Asset).where(Asset.id == asset_id)).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return asset

@router.post("", response_model=AssetSchema, status_code=201)
async def create_asset(
    asset_data: AssetCreateSchema,
    session: Session = Depends(get_session)
):
    """
    Create a new asset.
    
    **Fields:**
    - **id**: Unique asset identifier (required)
    - **asset_type**: Type of asset (Streetlight, Road & pavement, Drainage, Public space, Electrical)
    - **name**: Human-readable asset name
    - **ward**: Ward identifier
    - **latitude/longitude**: Optional geographic coordinates (validated: lat -90 to 90, lng -180 to 180)
    - **installation_date**: Optional installation date
    - **condition**: Asset condition (Good, Fair, Poor, Critical, default: Unknown)
    """
    # Check if asset already exists
    existing = session.exec(select(Asset).where(Asset.id == asset_data.id)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Asset {asset_data.id} already exists")
    
    asset = Asset(**asset_data.model_dump())
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset

@router.patch("/{asset_id}", response_model=AssetSchema)
async def patch_asset(
    asset_id: str,
    asset_data: AssetUpdateSchema,
    session: Session = Depends(get_session)
):
    """
    Update asset fields.
    
    **Allowed fields:**
    - **name**: Asset name
    - **condition**: Asset condition (Good, Fair, Poor, Critical)
    - **latitude/longitude**: Geographic coordinates
    - **installation_date**: Installation date
    """
    asset = session.exec(select(Asset).where(Asset.id == asset_id)).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    
    update_data = asset_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(asset, key, value)
    
    asset.updated_at = datetime.utcnow()
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset

@router.put("/{asset_id}", response_model=AssetSchema)
async def update_asset(
    asset_id: str,
    asset_data: AssetUpdateSchema,
    session: Session = Depends(get_session)
):
    """Update an existing asset (deprecated, use PATCH instead)."""
    asset = session.exec(select(Asset).where(Asset.id == asset_id)).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    
    update_data = asset_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(asset, key, value)
    
    asset.updated_at = datetime.utcnow()
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset
