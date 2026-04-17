"""Unified message sender dispatcher for multi-channel messaging."""

from typing import Dict, Any, Optional

from whatsapp_bot_shared import get_logger

from .meta_sender import MetaSenderService
from .twilio_service import get_twilio_service

logger = get_logger(__name__)


class MessageSender:
    """Unified message sender that routes to appropriate channel service."""

    @staticmethod
    async def send_message(
        channel: str,
        recipient_identifier: str,
        message_text: str,
        channel_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route message to correct sender based on channel.

        Args:
            channel: 'whatsapp', 'instagram', 'messenger'
            recipient_identifier: phone (+123...) for WhatsApp or PSID for Meta
            message_text: Text to send
            channel_config: Credentials dict with:
                - For Meta channels: page_access_token, page_id (required)
                - For WhatsApp: Twilio credentials (optional, falls back to env)

        Returns:
            {
                "status": "sent" | "failed",
                "channel": str,
                "recipient": str,
                "message_id": str | None,
                "error": str | None
            }

        Raises:
            ValueError: If channel is unsupported or required config is missing
        """
        channel = channel.lower()
        logger.info(f"Routing message to {channel} for recipient {recipient_identifier}")

        try:
            # WhatsApp via Twilio (sync)
            if channel == "whatsapp":
                twilio = get_twilio_service()
                result = twilio.send_message(recipient_identifier, message_text)

                # Normalize Twilio response format
                return {
                    "status": "sent" if result.get("status") in ["queued", "sent", "delivered"] else "failed",
                    "channel": "whatsapp",
                    "recipient": recipient_identifier,
                    "message_id": result.get("sid"),
                    "error": None
                }

            # Instagram/Messenger via Meta Graph API (async)
            elif channel in ["instagram", "messenger"]:
                # Validate required config
                if not channel_config:
                    raise ValueError(f"channel_config is required for {channel}")

                page_token = channel_config.get("page_access_token")
                page_id = channel_config.get("page_id")

                if not page_token:
                    raise ValueError(f"page_access_token is required in channel_config for {channel}")
                if not page_id:
                    raise ValueError(f"page_id is required in channel_config for {channel}")

                # Create Meta sender and send message
                from .meta_sender import Channel
                meta_channel = Channel.INSTAGRAM if channel == "instagram" else Channel.MESSENGER
                meta_sender = MetaSenderService(page_token, page_id, meta_channel)

                result = await meta_sender.send_message(recipient_identifier, message_text)

                # Add channel to response
                result["channel"] = channel

                # Normalize recipient key
                if "recipient_id" in result:
                    result["recipient"] = result.pop("recipient_id")

                return result

            # Unsupported channel
            else:
                raise ValueError(
                    f"Unsupported channel: {channel}. "
                    f"Supported channels: whatsapp, instagram, messenger"
                )

        except Exception as e:
            logger.error(f"Error sending message to {channel}: {e}")

            # Return normalized error response
            return {
                "status": "failed",
                "channel": channel,
                "recipient": recipient_identifier,
                "message_id": None,
                "error": str(e)
            }
