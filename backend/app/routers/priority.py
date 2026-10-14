"""Priority evaluation endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.complaint import Complaint
from app.services.priority_engine import get_evaluator
from app.schemas.priority import PriorityEvaluationSchema

router = APIRouter(prefix="/api/complaints", tags=["priority"])


@router.post("/{complaint_id}/priority/evaluate", response_model=PriorityEvaluationSchema)
async def evaluate_complaint_priority(
    complaint_id: str,
    session: Session = Depends(get_session)
):
    """
    Evaluate complaint priority using the priority engine.
    
    This endpoint evaluates the given complaint and returns a priority recommendation
    based on the configured priority engine (currently using mock/development engine).
    
    **Note:** In production, this would use your actual AI priority model.
    The mock engine includes a disclaimer in all scores.
    
    **Parameters:**
    - complaint_id: The complaint ID (e.g., CP-2026-0001)
    
    **Returns:** Priority evaluation with score, category, and explanation
    
    **Possible Responses:**
    - 200 OK: Priority evaluation successful
    - 404 Not Found: Complaint does not exist
    - 503 Service Unavailable: Priority engine not available (will return 200 with null score)
    """
    # Verify complaint exists
    complaint = session.exec(select(Complaint).where(Complaint.id == complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    
    # Prepare complaint data for evaluation
    complaint_data = {
        "id": complaint.id,
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category,
        "location_text": complaint.location_text,
        "latitude": complaint.latitude,
        "longitude": complaint.longitude,
        "ward": complaint.ward,
        "repeat_complaint_count": complaint.repeat_complaint_count,
        "reported_at": complaint.reported_at,
        "priority": complaint.priority,  # Current priority for reference
        "status": complaint.status
    }
    
    # Get evaluator and evaluate
    evaluator = get_evaluator()
    evaluation = evaluator.evaluate(complaint_data)
    
    if evaluation is None:
        # Engine unavailable, return 503 or graceful response
        raise HTTPException(
            status_code=503,
            detail="Priority engine not available. Please try again later."
        )
    
    return evaluation


@router.get("/{complaint_id}/priority", response_model=PriorityEvaluationSchema)
async def get_complaint_priority(
    complaint_id: str,
    session: Session = Depends(get_session)
):
    """
    Get priority evaluation for a complaint.
    
    This is a shorthand that performs priority evaluation on GET.
    In production with caching, this would retrieve cached evaluation.
    
    **Parameters:**
    - complaint_id: The complaint ID
    
    **Returns:** Priority evaluation
    """
    # Verify complaint exists
    complaint = session.exec(select(Complaint).where(Complaint.id == complaint_id)).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
    
    # Prepare data and evaluate
    complaint_data = {
        "id": complaint.id,
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category,
        "location_text": complaint.location_text,
        "latitude": complaint.latitude,
        "longitude": complaint.longitude,
        "ward": complaint.ward,
        "repeat_complaint_count": complaint.repeat_complaint_count,
        "reported_at": complaint.reported_at,
        "priority": complaint.priority,
        "status": complaint.status
    }
    
    # Evaluate
    evaluator = get_evaluator()
    evaluation = evaluator.evaluate(complaint_data)
    
    if evaluation is None:
        raise HTTPException(
            status_code=503,
            detail="Priority engine not available"
        )
    
    return evaluation
