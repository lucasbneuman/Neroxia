"""Twilio webhook router for receiving WhatsApp messages."""

import re
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.request_validator import RequestValidator

from neroxia_database import crud
from neroxia_shared import get_logger

from ..database import get_db
from .bot import process_bot_message, MessageRequest

logger = get_logger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


def extract_country_code(phone: str) -> Optional[str]:
    """
    Extract country code from phone number.
    
    Args:
        phone: Phone number in format +1234567890
        
    Returns:
        Country code (e.g., '+1', '+54', '+44') or None
    """
    match = re.match(r'(\+\d{1,3})', phone)
    return match.group(1) if match else None


@router.post("/twilio")
async def twilio_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    # Twilio sends data as form-encoded
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    ProfileName: Optional[str] = Form(None),
    NumMedia: Optional[str] = Form("0"),
    MediaUrl0: Optional[str] = Form(None),
    MediaContentType0: Optional[str] = Form(None),
    Latitude: Optional[str] = Form(None),
    Longitude: Optional[str] = Form(None),
    Address: Optional[str] = Form(None),
):
    """
    Receive incoming WhatsApp messages from Twilio.
    
    Twilio sends webhooks with the following data:
    - From: User's phone number (format: whatsapp:+1234567890)
    - To: Your WhatsApp Business number
    - Body: Message text
    - MessageSid: Unique message ID
    - ProfileName: WhatsApp profile name (IMPORTANT!)
    - NumMedia: Number of media files
    - MediaUrl0, MediaUrl1, etc.: URLs to media files
    - Latitude, Longitude, Address: Location data if shared
    
    This endpoint:
    1. Extracts all available Twilio data
    2. Creates or updates user with Twilio data
    3. Processes message through bot
    4. Responds via Twilio
    """
    try:
        logger.info(f"Received Twilio webhook from {From}")
        
        # Clean phone number (remove 'whatsapp:' prefix)
        phone = From.replace("whatsapp:", "")
        
        # Extract country code
        country_code = extract_country_code(phone)
        
        # Parse media count
        num_media = int(NumMedia) if NumMedia else 0
        
        # Check if location was shared
        location_shared = bool(Latitude and Longitude)

        # Get or create user with Twilio data (atomic operation)
        user, created = await crud.get_or_create_user(
            db=db,
            identifier=phone,
            channel="whatsapp",
            auth_user_id=None,  # Twilio webhooks are not tenant-scoped
            defaults={
                "whatsapp_profile_name": ProfileName,
                "country_code": country_code,
                "phone_formatted": phone,
                "first_contact_timestamp": datetime.utcnow(),
            }
        )

        if created:
            logger.info(f"✅ Created user with WhatsApp profile name: {ProfileName}")
        else:
            # Update existing user with Twilio data
            logger.info(f"Updating existing user from Twilio webhook: {phone}")
            await crud.update_user_from_twilio(
                db=db,
                user_id=user.id,
                whatsapp_profile_name=ProfileName,
                media_count_increment=num_media,
                location_shared=location_shared,
                last_twilio_message_sid=MessageSid,
            )
            logger.info(f"✅ Updated user with Twilio data")
        
        # If user shared location, log it
        if location_shared:
            logger.info(f"📍 User shared location: {Latitude}, {Longitude} - {Address}")
        
        # If user sent media, log it
        if num_media > 0:
            logger.info(f"📎 User sent {num_media} media file(s)")
            if MediaUrl0:
                logger.info(f"   Media URL: {MediaUrl0} ({MediaContentType0})")
        
        # Process message through bot
        # We use the existing bot processing endpoint logic
        message_request = MessageRequest(
            phone=phone,
            message=Body,
            config={},  # Will load from DB
            history=None,  # Will load from DB
        )
        
        # Process through bot engine
        from .bot import process_bot_message as process_message_func
        bot_response = await process_message_func(message_request, db)
        
        # Return TwiML response
        # Twilio expects XML response with <Message> tag
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{bot_response.response}</Message>
</Response>"""
        
        logger.info(f"✅ Sent response to {phone} via Twilio")
        
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing Twilio webhook: {e}", exc_info=True)
        
        # Return error response in TwiML format
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Lo siento, hubo un error procesando tu mensaje. Por favor intenta de nuevo.</Message>
</Response>"""
        
        return Response(content=error_response, media_type="application/xml", status_code=200)


@router.get("/twilio/status")
async def twilio_webhook_status():
    """
    Check if Twilio webhook endpoint is available.
    
    This endpoint can be used to verify that the webhook is configured correctly.
    """
    return {
        "status": "active",
        "endpoint": "/webhook/twilio",
        "method": "POST",
        "description": "Twilio WhatsApp webhook endpoint",
        "data_collected": [
            "phone_number",
            "whatsapp_profile_name",
            "country_code",
            "media_files",
            "location",
            "message_sid",
        ],
    }
