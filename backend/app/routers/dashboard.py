"""Dashboard and analytics endpoints."""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from app.database import get_session
from app.models.complaint import Complaint
from app.models.asset import Asset
from app.models.repair import RepairRecord
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    session: Session = Depends(get_session),
    days: int = Query(30, ge=1, le=365, description="Number of days to include in recent stats")
) -> Dict[str, Any]:
    """
    Get overall dashboard statistics.
    
    Returns:
    - Total complaints and open/unresolved counts
    - Verified resolutions
    - Status distribution
    - Category breakdown
    - Recent activity metrics
    
    **Parameters:**
    - days: Include activity from the last N days (default: 30, max: 365)
    """
    # Total complaint counts
    total_complaints = len(session.exec(select(Complaint)).all())
    
    # Open/unresolved complaints
    open_statuses = {"Reported", "Under Review", "Assigned", "In Progress", "Awaiting Verification"}
    unresolved = len(session.exec(
        select(Complaint).where(Complaint.status.in_(open_statuses))
    ).all())
    
    # Resolved complaints
    resolved = len(session.exec(
        select(Complaint).where(Complaint.status == "Resolved")
    ).all())
    
    # Recent complaints (within N days)
    days_ago = datetime.utcnow() - timedelta(days=days)
    recent = len(session.exec(
        select(Complaint).where(Complaint.reported_at >= days_ago)
    ).all())
    
    # Status distribution
    status_distribution = {}
    for status in ["Reported", "Under Review", "Assigned", "In Progress", "Awaiting Verification", "Resolved"]:
        count = len(session.exec(
            select(Complaint).where(Complaint.status == status)
        ).all())
        if count > 0:
            status_distribution[status] = count
    
    # Category breakdown
    category_distribution = {}
    all_complaints = session.exec(select(Complaint)).all()
    for complaint in all_complaints:
        category = complaint.category or "Uncategorized"
        category_distribution[category] = category_distribution.get(category, 0) + 1
    
    # Repeat complaints
    high_repeat = len([c for c in all_complaints if c.repeat_complaint_count > 2])
    
    # Average priority score
    priority_scores = [c.priority_score for c in all_complaints if c.priority_score]
    avg_priority = sum(priority_scores) / len(priority_scores) if priority_scores else 0
    
    # Repair statistics
    all_repairs = session.exec(select(RepairRecord)).all()
    verified_repairs = len([r for r in all_repairs if r.verification_status == "Verified"])
    failed_repairs = len([r for r in all_repairs if r.verification_status == "Failed"])
    
    # Teams active
    teams = set()
    for complaint in all_complaints:
        if complaint.assigned_team:
            teams.add(complaint.assigned_team)
    for repair in all_repairs:
        if repair.assigned_team:
            teams.add(repair.assigned_team)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "period_days": days,
        "complaints": {
            "total": total_complaints,
            "open": unresolved,
            "resolved": resolved,
            "recent": recent,
            "high_repeat_issues": high_repeat,
            "average_priority_score": round(avg_priority, 2)
        },
        "status_distribution": status_distribution,
        "category_distribution": category_distribution,
        "repairs": {
            "total_records": len(all_repairs),
            "verified": verified_repairs,
            "failed": failed_repairs,
            "pending": len([r for r in all_repairs if r.verification_status == "Pending"]),
            "rejected": len([r for r in all_repairs if r.verification_status == "Rejected"])
        },
        "teams_active": len(teams),
        "response_time_metrics": {
            "note": "Response time tracking coming in Phase 3"
        }
    }


@router.get("/priority-summary")
async def get_priority_summary(
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get priority level distribution for all complaints.
    
    Returns:
    - Count and percentage breakdown by priority level
    - Unassigned complaints
    - Complaints by priority and status
    """
    all_complaints = session.exec(select(Complaint)).all()
    total = len(all_complaints)
    
    if total == 0:
        return {
            "total_complaints": 0,
            "by_priority": {},
            "distribution_percentage": {},
            "by_priority_and_status": {},
            "unassigned_by_priority": {}
        }
    
    # Priority distribution
    priority_dist = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for complaint in all_complaints:
        priority = complaint.priority or "Unknown"
        if priority in priority_dist:
            priority_dist[priority] += 1
    
    # Calculate percentages
    distribution_pct = {
        priority: round((count / total * 100), 2)
        for priority, count in priority_dist.items()
        if count > 0
    }
    
    # Priority and status breakdown
    priority_status = {}
    for complaint in all_complaints:
        key = f"{complaint.priority}_{complaint.status}"
        priority_status[key] = priority_status.get(key, 0) + 1
    
    # Unassigned complaints by priority
    unassigned_by_priority = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for complaint in all_complaints:
        if not complaint.assigned_team:
            priority = complaint.priority or "Unknown"
            if priority in unassigned_by_priority:
                unassigned_by_priority[priority] += 1
    
    return {
        "total_complaints": total,
        "by_priority": priority_dist,
        "distribution_percentage": distribution_pct,
        "by_priority_and_status": priority_status,
        "unassigned_by_priority": unassigned_by_priority,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/asset-summary")
async def get_asset_summary(
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get asset inventory and condition summary.
    
    Returns:
    - Asset count by type and condition
    - Geographic distribution (wards)
    - Asset health metrics
    - Assets with active complaints
    """
    all_assets = session.exec(select(Asset)).all()
    all_complaints = session.exec(select(Complaint)).all()
    
    total_assets = len(all_assets)
    
    if total_assets == 0:
        return {
            "total_assets": 0,
            "by_type": {},
            "by_condition": {},
            "by_ward": {},
            "with_complaints": 0,
            "with_valid_coordinates": 0
        }
    
    # Asset type distribution
    asset_type_dist = {}
    for asset in all_assets:
        asset_type = asset.asset_type or "Unknown"
        asset_type_dist[asset_type] = asset_type_dist.get(asset_type, 0) + 1
    
    # Condition distribution
    condition_dist = {}
    for asset in all_assets:
        condition = asset.condition or "Unknown"
        condition_dist[condition] = condition_dist.get(condition, 0) + 1
    
    # Ward distribution
    ward_dist = {}
    for asset in all_assets:
        ward = asset.ward or "Unknown"
        ward_dist[ward] = ward_dist.get(ward, 0) + 1
    
    # Assets with complaints
    asset_ids_with_complaints = set(c.asset_id for c in all_complaints if c.asset_id)
    assets_with_complaints = len(asset_ids_with_complaints)
    
    # Assets with valid coordinates
    assets_with_coords = len([a for a in all_assets if a.latitude and a.longitude])
    
    # Condition scoring (Good=0, Fair=1, Poor=2, Critical=3)
    health_scores = {
        "Good": 0,
        "Fair": 1,
        "Poor": 2,
        "Critical": 3,
        "Unknown": 1.5  # Neutral
    }
    avg_health_score = sum(
        health_scores.get(a.condition or "Unknown", 1.5)
        for a in all_assets
    ) / total_assets if total_assets > 0 else 0
    
    # Health status
    if avg_health_score < 1:
        health_status = "Good"
    elif avg_health_score < 1.5:
        health_status = "Fair"
    elif avg_health_score < 2.5:
        health_status = "Poor"
    else:
        health_status = "Critical"
    
    return {
        "total_assets": total_assets,
        "by_type": asset_type_dist,
        "by_condition": condition_dist,
        "by_ward": ward_dist,
        "with_complaints": assets_with_complaints,
        "with_valid_coordinates": assets_with_coords,
        "health_status": health_status,
        "average_health_score": round(avg_health_score, 2),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/map-data")
async def get_map_data(
    session: Session = Depends(get_session),
    include_complaints: bool = Query(True, description="Include complaint markers"),
    include_assets: bool = Query(True, description="Include asset markers"),
    priority_filter: str = Query(None, description="Filter by priority (Low, Medium, High, Critical)"),
    status_filter: str = Query(None, description="Filter by status"),
    asset_type_filter: str = Query(None, description="Filter assets by type"),
    ward_filter: str = Query(None, description="Filter by ward"),
    coordinates_only: bool = Query(False, description="Only include items with valid coordinates")
) -> Dict[str, Any]:
    """
    Get geographic data for map rendering.
    
    Returns complaints and assets with coordinates for map markers.
    
    **Filters:**
    - priority_filter: For complaints only
    - status_filter: For complaints only
    - asset_type_filter: For assets only
    - ward_filter: Applied to both
    - coordinates_only: Exclude items without valid coordinates
    """
    complaints_data = []
    assets_data = []
    
    if include_complaints:
        query = select(Complaint)
        
        if priority_filter:
            query = query.where(Complaint.priority == priority_filter)
        if status_filter:
            query = query.where(Complaint.status == status_filter)
        if ward_filter:
            query = query.where(Complaint.ward == ward_filter)
        
        complaints = session.exec(query).all()
        
        for complaint in complaints:
            if coordinates_only and not (complaint.latitude and complaint.longitude):
                continue
            
            complaints_data.append({
                "id": complaint.id,
                "type": "complaint",
                "title": complaint.title,
                "category": complaint.category,
                "priority": complaint.priority,
                "status": complaint.status,
                "latitude": complaint.latitude,
                "longitude": complaint.longitude,
                "location_text": complaint.location_text,
                "ward": complaint.ward,
                "has_coordinates": complaint.latitude is not None and complaint.longitude is not None
            })
    
    if include_assets:
        query = select(Asset)
        
        if asset_type_filter:
            query = query.where(Asset.asset_type == asset_type_filter)
        if ward_filter:
            query = query.where(Asset.ward == ward_filter)
        
        assets = session.exec(query).all()
        
        for asset in assets:
            if coordinates_only and not (asset.latitude and asset.longitude):
                continue
            
            assets_data.append({
                "id": asset.id,
                "type": "asset",
                "name": asset.name,
                "asset_type": asset.asset_type,
                "condition": asset.condition,
                "latitude": asset.latitude,
                "longitude": asset.longitude,
                "ward": asset.ward,
                "has_coordinates": asset.latitude is not None and asset.longitude is not None
            })
    
    return {
        "complaints": complaints_data,
        "assets": assets_data,
        "total_markers": len(complaints_data) + len(assets_data),
        "timestamp": datetime.utcnow().isoformat(),
        "filters_applied": {
            "priority_filter": priority_filter,
            "status_filter": status_filter,
            "asset_type_filter": asset_type_filter,
            "ward_filter": ward_filter,
            "coordinates_only": coordinates_only
        }
    }
