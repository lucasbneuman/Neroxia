"""Follow-up scheduling router."""

import sys
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from whatsapp_bot_shared import get_logger

# Add bot-engine to Python path
bot_engine_path = Path(__file__).parent.parent.parent.parent / "bot-engine" / "src"
if str(bot_engine_path) not in sys.path:
    sys.path.insert(0, str(bot_engine_path))

# Import bot-engine services (with graceful error handling)
try:
    from services.scheduler_service import get_scheduler_service
    SCHEDULER_AVAILABLE = True
except ImportError as e:
    logger = get_logger(__name__)
    logger.warning(f"Scheduler service not available: {e}")
    SCHEDULER_AVAILABLE = False
    get_scheduler_service = None

from .auth import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/followups", tags=["followups"])


class ScheduleFollowUpRequest(BaseModel):
    """Follow-up scheduling request."""
    message: str
    scheduled_time: datetime


class FollowUpInfo(BaseModel):
    """Follow-up job information."""
    id: str
    next_run_time: datetime | None
    trigger: str


async def send_followup_message(phone: str, message: str):
    """
    Send a follow-up message.
    
    This is a placeholder function that would integrate with Twilio/WhatsApp service.
    For now, it just logs the message.
    """
    logger.info(f"Sending follow-up to {phone}: {message}")
    # TODO: Integrate with Twilio service to actually send the message
    # from services.twilio_service import get_twilio_service
    # twilio_service = get_twilio_service()
    # await twilio_service.send_message(phone, message)


@router.get("/")
async def list_followups(
    current_user: dict = Depends(get_current_user)
) -> List[FollowUpInfo]:
    """
    List all scheduled follow-ups.
    
    Returns information about all pending follow-up jobs.
    """
    if not SCHEDULER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Scheduler service is not available. Install apscheduler to enable follow-ups."
        )
    
    try:
        scheduler_service = get_scheduler_service()
        jobs = scheduler_service.get_all_jobs()
        
        logger.info(f"Retrieved {len(jobs)} scheduled follow-ups")
        
        return [
            FollowUpInfo(
                id=job["id"],
                next_run_time=job["next_run_time"],
                trigger=job["trigger"]
            )
            for job in jobs
        ]
    
    except Exception as e:
        logger.error(f"Error listing follow-ups: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list follow-ups: {str(e)}"
        )


@router.post("/{phone}/schedule")
async def schedule_followup(
    phone: str,
    request: ScheduleFollowUpRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Schedule a follow-up message.
    
    Creates a scheduled job to send a message at the specified time.
    """
    if not SCHEDULER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Scheduler service is not available. Install apscheduler to enable follow-ups."
        )
    
    try:
        scheduler_service = get_scheduler_service()
        
        # Generate job ID
        job_id = f"followup_{phone}_{int(request.scheduled_time.timestamp())}"
        
        # Schedule the job
        await scheduler_service.add_follow_up_job(
            job_id=job_id,
            phone=phone,
            message=request.message,
            scheduled_time=request.scheduled_time,
            send_function=send_followup_message
        )
        
        logger.info(f"Scheduled follow-up {job_id} for {phone} at {request.scheduled_time}")
        
        return {
            "status": "success",
            "job_id": job_id,
            "phone": phone,
            "message": request.message,
            "scheduled_time": request.scheduled_time
        }
    
    except Exception as e:
        logger.error(f"Error scheduling follow-up: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to schedule follow-up: {str(e)}"
        )


@router.delete("/{job_id}")
async def cancel_followup(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel a scheduled follow-up.
    
    Removes the scheduled job from the queue.
    """
    if not SCHEDULER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Scheduler service is not available. Install apscheduler to enable follow-ups."
        )
    
    try:
        scheduler_service = get_scheduler_service()
        
        success = scheduler_service.cancel_follow_up_job(job_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Follow-up job not found: {job_id}"
            )
        
        logger.info(f"Cancelled follow-up: {job_id}")
        
        return {
            "status": "success",
            "message": f"Follow-up {job_id} cancelled successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling follow-up: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel follow-up: {str(e)}"
        )


@router.get("/{job_id}")
async def get_followup(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get information about a specific follow-up.
    
    Returns details about a scheduled follow-up job.
    """
    if not SCHEDULER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Scheduler service is not available. Install apscheduler to enable follow-ups."
        )
    
    try:
        scheduler_service = get_scheduler_service()
        
        job_info = scheduler_service.get_job_info(job_id)
        
        if not job_info:
            raise HTTPException(
                status_code=404,
                detail=f"Follow-up job not found: {job_id}"
            )
        
        return FollowUpInfo(
            id=job_info["id"],
            next_run_time=job_info["next_run_time"],
            trigger=job_info["trigger"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting follow-up info: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get follow-up info: {str(e)}"
        )
