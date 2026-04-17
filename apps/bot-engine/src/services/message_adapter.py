"""
Message adapter to normalize messages from different channels.

Converts channel-specific message formats to a unified internal format
that the LangGraph workflow can process.
"""

from typing import Dict, Any
from datetime import datetime


class MessageAdapter:
    """Adapter pattern for normalizing multi-channel messages."""

    @staticmethod
    def normalize_message(channel: str, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize incoming message to unified format.

        Args:
            channel: "whatsapp", "instagram", or "messenger"
            raw_payload: Raw webhook payload from channel

        Returns:
            {
                "channel": str,
                "user_id": str,  # phone or PSID
                "message_text": str,
                "timestamp": datetime,
                "metadata": dict  # channel-specific data
            }
        """
        if channel == "whatsapp":
            return MessageAdapter._normalize_twilio(raw_payload)
        elif channel == "instagram":
            return MessageAdapter._normalize_instagram(raw_payload)
        elif channel == "messenger":
            return MessageAdapter._normalize_messenger(raw_payload)
        else:
            raise ValueError(f"Unsupported channel: {channel}")

    @staticmethod
    def _normalize_twilio(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Twilio WhatsApp webhook."""
        return {
            "channel": "whatsapp",
            "user_id": payload.get("From", "").replace("whatsapp:", ""),
            "message_text": payload.get("Body", ""),
            "timestamp": datetime.utcnow(),
            "metadata": {
                "message_sid": payload.get("MessageSid"),
                "profile_name": payload.get("ProfileName"),
                "num_media": payload.get("NumMedia", 0)
            }
        }

    @staticmethod
    def _normalize_instagram(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Instagram webhook."""
        sender = payload.get("sender", {})
        message = payload.get("message", {})

        return {
            "channel": "instagram",
            "user_id": sender.get("id"),
            "message_text": message.get("text", ""),
            "timestamp": datetime.fromtimestamp(payload.get("timestamp", 0) / 1000),
            "metadata": {
                "message_id": message.get("mid"),
                "page_id": payload.get("recipient", {}).get("id"),
                "has_attachments": "attachments" in message
            }
        }

    @staticmethod
    def _normalize_messenger(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Messenger webhook (similar structure to Instagram)."""
        sender = payload.get("sender", {})
        message = payload.get("message", {})

        return {
            "channel": "messenger",
            "user_id": sender.get("id"),
            "message_text": message.get("text", ""),
            "timestamp": datetime.fromtimestamp(payload.get("timestamp", 0) / 1000),
            "metadata": {
                "message_id": message.get("mid"),
                "page_id": payload.get("recipient", {}).get("id"),
                "has_attachments": "attachments" in message
            }
        }
