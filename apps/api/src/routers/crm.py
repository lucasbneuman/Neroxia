"""CRM API Router."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from whatsapp_bot_database import crud
from whatsapp_bot_shared import get_logger

from ..database import get_db
from .auth import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/crm", tags=["crm"])


# ============================================================================
# Pydantic Models
# ============================================================================

class DealCreate(BaseModel):
    user_id: int
    title: str
    value: float = 0.0
    stage: str = "new_lead"
    source: str = "whatsapp"
    probability: int = 10
    expected_close_date: Optional[datetime] = None

class DealUpdate(BaseModel):
    title: Optional[str] = None
    value: Optional[float] = None
    stage: Optional[str] = None
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None

class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)
    note_type: str = "note"
    deal_id: Optional[int] = None
    created_by: str = "test-user-id-123"

class TagCreate(BaseModel):
    name: str
    color: str = "#6B7280"


class DealLostRequest(BaseModel):
    reason: str


# ============================================================================
# Dashboard Endpoints
# ============================================================================

@router.get("/dashboard/metrics")
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get CRM dashboard metrics."""
    try:
        return await crud.get_crm_metrics(db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CRM metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Deal Endpoints
# ============================================================================

@router.get("/deals")
async def get_deals(
    stage: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all deals."""
    try:
        deals = await crud.get_all_deals(db, stage=stage, limit=limit, offset=offset)
        return deals
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deals")
async def create_deal(
    deal: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new deal."""
    try:
        return await crud.create_deal(
            db,
            user_id=deal.user_id,
            title=deal.title,
            value=deal.value,
            stage=deal.stage,
            source=deal.source,
            probability=deal.probability,
            expected_close_date=deal.expected_close_date
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating deal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deals/{deal_id}")
async def get_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get deal by ID."""
    deal = await crud.get_deal_by_id(db, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal



class DealStageUpdate(BaseModel):
    stage: str

@router.patch("/deals/{deal_id}")
async def update_deal(
    deal_id: int,
    deal_update: DealUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update a deal."""
    try:
        # Filter out None values
        update_data = {k: v for k, v in deal_update.dict().items() if v is not None}
        updated_deal = await crud.update_deal(db, deal_id, **update_data)
        if not updated_deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        return updated_deal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating deal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/deals/{deal_id}/stage")
async def update_deal_stage(
    deal_id: int,
    stage_update: DealStageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update deal stage."""
    try:
        updated_deal = await crud.update_deal(db, deal_id, stage=stage_update.stage)
        if not updated_deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        return updated_deal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating deal stage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deals/{deal_id}/won")
async def mark_deal_won(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark deal as won."""
    try:
        updated_deal = await crud.mark_deal_won(db, deal_id)
        if not updated_deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        return updated_deal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking deal as won: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deals/{deal_id}/lost")
async def mark_deal_lost(
    deal_id: int,
    payload: DealLostRequest | None = None,
    reason: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark deal as lost."""
    try:
        lost_reason = reason or (payload.reason if payload else None)
        if not lost_reason:
            raise HTTPException(status_code=422, detail="reason is required")
        updated_deal = await crud.mark_deal_lost(db, deal_id, lost_reason)
        if not updated_deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        return updated_deal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking deal as lost: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/deals/{deal_id}")
async def delete_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a deal."""
    try:
        success = await crud.delete_deal(db, deal_id)
        if not success:
            raise HTTPException(status_code=404, detail="Deal not found")
        return {"status": "success", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting deal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Note Endpoints
# ============================================================================

@router.get("/users/{user_id}/notes")
async def get_user_notes(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get notes for a user."""
    try:
        return await crud.get_user_notes(db, user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/notes")
async def create_note(
    user_id: int,
    note: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new note."""
    try:
        return await crud.create_note(
            db,
            user_id=user_id,
            content=note.content,
            created_by=note.created_by,
            deal_id=note.deal_id,
            note_type=note.note_type
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a note."""
    try:
        success = await crud.delete_note(db, note_id)
        if not success:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"status": "success", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Tag Endpoints
# ============================================================================

@router.get("/tags")
async def get_tags(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all tags."""
    try:
        return await crud.get_all_tags(db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tags")
async def create_tag(
    tag: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new tag."""
    try:
        return await crud.create_tag(db, name=tag.name, color=tag.color)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/tags")
async def get_user_tags(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get tags for a user."""
    try:
        return await crud.get_user_tags(db, user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/tags/{tag_id}")
async def add_tag_to_user(
    user_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Assign tag to user."""
    try:
        return await crud.add_tag_to_user(db, user_id, tag_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}/tags/{tag_id}")
async def remove_tag_from_user(
    user_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Remove tag from user."""
    try:
        success = await crud.remove_tag_from_user(db, user_id, tag_id)
        if not success:
            raise HTTPException(status_code=404, detail="Tag assignment not found")
        return {"status": "success", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))
