"""Meta Graph API sender service for Instagram and Messenger."""

import asyncio
from typing import Dict, Any, Optional
from enum import Enum

try:
    import httpx
except ImportError:
    httpx = None

from whatsapp_bot_shared import get_logger

logger = get_logger(__name__)


class Channel(str, Enum):
    """Supported Meta channels."""
    INSTAGRAM = "instagram"
    MESSENGER = "messenger"


class MetaSenderService:
    """Send messages via Meta Graph API for Instagram and Messenger."""

    # Character limits per channel
    CHAR_LIMITS = {
        Channel.INSTAGRAM: 1000,
        Channel.MESSENGER: 2000,
    }

    # Meta Graph API version
    API_VERSION = "v18.0"

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # Exponential backoff in seconds

    def __init__(self, page_access_token: str, page_id: str, channel: Channel = Channel.INSTAGRAM):
        """
        Initialize with page-specific credentials from ChannelIntegration.

        Args:
            page_access_token: Page access token from Meta
            page_id: Facebook Page ID
            channel: Channel type (instagram or messenger)
        """
        if httpx is None:
            raise ImportError(
                "httpx is required for MetaSenderService. "
                "Install it with: pip install httpx"
            )

        self.page_access_token = page_access_token
        self.page_id = page_id
        self.channel = channel
        self.base_url = f"https://graph.facebook.com/{self.API_VERSION}/{page_id}/messages"
        self.char_limit = self.CHAR_LIMITS[channel]

        logger.info(
            f"MetaSenderService initialized for {channel.value} "
            f"(page_id={page_id}, limit={self.char_limit} chars)"
        )

    async def send_message(
        self,
        recipient_id: str,
        message_text: str,
        truncate: bool = True
    ) -> Dict[str, Any]:
        """
        Send text message via Meta Graph API.

        POST https://graph.facebook.com/v18.0/{page-id}/messages
        {
            "recipient": {"id": "<PSID>"},
            "message": {"text": "..."}
        }

        Args:
            recipient_id: Page-Scoped ID (PSID) of the recipient
            message_text: Text message to send
            truncate: Whether to truncate message if exceeds limit (default: True)

        Returns:
            {
                "status": "sent" | "failed",
                "recipient_id": str,
                "message_id": str | None,  # From Meta response
                "error": str | None
            }
        """
        # Handle character limit
        if len(message_text) > self.char_limit:
            if truncate:
                message_text = self._truncate_message(message_text, self.char_limit)
                logger.warning(
                    f"Message truncated to {self.char_limit} chars for {self.channel.value}"
                )
            else:
                return {
                    "status": "failed",
                    "recipient_id": recipient_id,
                    "message_id": None,
                    "error": f"Message exceeds {self.char_limit} character limit"
                }

        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }

        # Send with retry logic
        return await self._send_with_retry(recipient_id, payload)

    async def send_typing_indicator(
        self,
        recipient_id: str,
        typing_on: bool = True
    ) -> Dict[str, Any]:
        """
        Send typing indicator for better UX.

        Args:
            recipient_id: Page-Scoped ID (PSID) of the recipient
            typing_on: True to show typing, False to hide

        Returns:
            {
                "status": "sent" | "failed",
                "recipient_id": str,
                "message_id": None,
                "error": str | None
            }
        """
        sender_action = "typing_on" if typing_on else "typing_off"

        payload = {
            "recipient": {"id": recipient_id},
            "sender_action": sender_action
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.base_url,
                    params={"access_token": self.page_access_token},
                    json=payload
                )

                if response.status_code == 200:
                    logger.debug(
                        f"Typing indicator {sender_action} sent to {recipient_id}"
                    )
                    return {
                        "status": "sent",
                        "recipient_id": recipient_id,
                        "message_id": None,
                        "error": None
                    }
                else:
                    error_detail = response.json() if response.text else {}
                    logger.error(
                        f"Failed to send typing indicator: {response.status_code} - {error_detail}"
                    )
                    return {
                        "status": "failed",
                        "recipient_id": recipient_id,
                        "message_id": None,
                        "error": f"HTTP {response.status_code}: {error_detail}"
                    }

        except Exception as e:
            logger.error(f"Exception sending typing indicator: {e}")
            return {
                "status": "failed",
                "recipient_id": recipient_id,
                "message_id": None,
                "error": str(e)
            }

    async def _send_with_retry(
        self,
        recipient_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send message with exponential backoff retry logic.

        Retries on:
        - HTTP 429 (rate limit)
        - Specific Meta API error codes for rate limiting

        Args:
            recipient_id: Page-Scoped ID
            payload: Request payload

        Returns:
            Response dict with status, message_id, and error
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        self.base_url,
                        params={"access_token": self.page_access_token},
                        json=payload
                    )

                    # Success case
                    if response.status_code == 200:
                        data = response.json()
                        message_id = data.get("message_id")

                        logger.info(
                            f"Message sent successfully to {recipient_id} "
                            f"(message_id={message_id})"
                        )

                        return {
                            "status": "sent",
                            "recipient_id": recipient_id,
                            "message_id": message_id,
                            "error": None
                        }

                    # Rate limit - retry with backoff
                    elif response.status_code == 429:
                        last_error = "Rate limit exceeded"
                        logger.warning(
                            f"Rate limit hit (attempt {attempt + 1}/{self.MAX_RETRIES})"
                        )

                        if attempt < self.MAX_RETRIES - 1:
                            delay = self.RETRY_DELAYS[attempt]
                            logger.info(f"Retrying in {delay}s...")
                            await asyncio.sleep(delay)
                            continue

                    # Check for Meta API rate limit error codes
                    else:
                        error_data = response.json() if response.text else {}
                        error_code = error_data.get("error", {}).get("code")
                        error_message = error_data.get("error", {}).get("message", "Unknown error")

                        # Meta rate limit error codes: 4, 17, 32, 613
                        if error_code in [4, 17, 32, 613] and attempt < self.MAX_RETRIES - 1:
                            last_error = f"Meta API error {error_code}: {error_message}"
                            logger.warning(
                                f"Rate limit error (code={error_code}, "
                                f"attempt {attempt + 1}/{self.MAX_RETRIES})"
                            )

                            delay = self.RETRY_DELAYS[attempt]
                            logger.info(f"Retrying in {delay}s...")
                            await asyncio.sleep(delay)
                            continue

                        # Other errors - don't retry
                        else:
                            last_error = f"HTTP {response.status_code}: {error_message}"
                            logger.error(
                                f"Failed to send message: {last_error} (error_code={error_code})"
                            )
                            break

            except httpx.TimeoutException:
                last_error = "Request timeout"
                logger.error(f"Timeout sending message (attempt {attempt + 1}/{self.MAX_RETRIES})")

                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAYS[attempt]
                    await asyncio.sleep(delay)
                    continue

            except Exception as e:
                last_error = str(e)
                logger.error(f"Exception sending message: {e}")
                break

        # All retries exhausted or non-retryable error
        return {
            "status": "failed",
            "recipient_id": recipient_id,
            "message_id": None,
            "error": last_error or "Unknown error"
        }

    @staticmethod
    def _truncate_message(text: str, limit: int) -> str:
        """
        Truncate message to limit with ellipsis.

        Args:
            text: Message text
            limit: Character limit

        Returns:
            Truncated text with "..." if needed
        """
        if len(text) <= limit:
            return text
        return text[:limit - 3] + "..."
