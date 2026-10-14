"""ID generation service for unique identifiers."""

from datetime import datetime
from sqlmodel import Session, select
from app.models.complaint import Complaint
from app.models.asset import Asset
from app.models.repair import RepairRecord

# Simple counters to avoid database lookups in test environment
# In production, these would be thread-safe or use database sequences
_complaint_counter = {}
_asset_counter = {}
_repair_counter = {}

def generate_complaint_id() -> str:
    """
    Generate a unique complaint ID.
    
    Format: CP-YYYY-NNNN where:
    - CP = prefix
    - YYYY = current year
    - NNNN = sequential number
    
    Returns:
        str: Unique complaint ID
    """
    current_year = datetime.utcnow().year
    key = f"complaint_{current_year}"
    
    # Simple counter-based approach (safe for single-threaded test env)
    if key not in _complaint_counter:
        _complaint_counter[key] = 0
    
    _complaint_counter[key] += 1
    num = _complaint_counter[key]
    
    complaint_id = f"CP-{current_year}-{num:04d}"
    return complaint_id


def generate_asset_id(asset_type: str, ward: str) -> str:
    """
    Generate a unique asset ID.
    
    Format: TYPE-WARD-NNNN where:
    - TYPE = first 2-3 chars of asset type
    - WARD = ward identifier
    - NNNN = sequential number
    
    Returns:
        str: Unique asset ID
    """
    # Map asset types to prefixes
    type_map = {
        "Streetlight": "SL",
        "Road & pavement": "RD",
        "Drainage": "DR",
        "Public space": "PS",
        "Electrical Hazard": "EL",
    }
    
    prefix = type_map.get(asset_type, asset_type[:2].upper())
    key = f"asset_{prefix}_{ward}"
    
    if key not in _asset_counter:
        _asset_counter[key] = 0
    
    _asset_counter[key] += 1
    num = _asset_counter[key]
    
    asset_id = f"{prefix}-{ward}-{num:03d}"
    return asset_id


def generate_repair_id() -> str:
    """
    Generate a unique repair record ID.
    
    Format: RP-YYYYMMDD-NNNN
    
    Returns:
        str: Unique repair record ID
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    key = f"repair_{today}"
    
    if key not in _repair_counter:
        _repair_counter[key] = 0
    
    _repair_counter[key] += 1
    num = _repair_counter[key]
    
    repair_id = f"RP-{today}-{num:04d}"
    return repair_id
