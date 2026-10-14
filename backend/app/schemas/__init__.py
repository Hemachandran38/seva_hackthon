"""API schemas for request/response validation."""

from app.schemas.asset import AssetSchema, AssetCreateSchema, AssetUpdateSchema
from app.schemas.complaint import (
    ComplaintSchema,
    ComplaintCreateSchema,
    ComplaintUpdateSchema,
    ComplaintTimelineSchema,
)
from app.schemas.repair import RepairRecordSchema, RepairRecordCreateSchema
from app.schemas.common import PaginatedResponse

__all__ = [
    "AssetSchema",
    "AssetCreateSchema",
    "AssetUpdateSchema",
    "ComplaintSchema",
    "ComplaintCreateSchema",
    "ComplaintUpdateSchema",
    "ComplaintTimelineSchema",
    "RepairRecordSchema",
    "RepairRecordCreateSchema",
    "PaginatedResponse",
]
