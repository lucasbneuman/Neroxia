"""Public web widget endpoints and embeddable script delivery."""

from __future__ import annotations

import base64
import json
import os
import secrets
from typing import Any, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from whatsapp_bot_database import crud

from ..core.widget_security import (
    WIDGET_CONFIG_KEY,
    build_widget_session_payload,
    is_origin_allowed,
    parse_widget_id,
    sign_widget_session,
    verify_widget_session,
)
from ..core.rate_limit import limiter
from ..database import get_db
from ..services.message_processing import process_incoming_message

router = APIRouter(tags=["widget"])


class WidgetBootstrapRequest(BaseModel):
    """Widget bootstrap payload."""
    widget_id: str
    origin: str
    page_url: str
    session_id: Optional[str] = None


class WidgetMessageRequest(BaseModel):
    """Widget message payload."""
    token: str
    message: str = Field(..., min_length=1)
    page_url: str


def _frontend_url() -> str:
    return os.getenv("FRONTEND_URL") or "http://localhost:3000"


async def _load_widget_config(db: AsyncSession, widget_id: str) -> tuple[str, dict[str, Any]]:
    auth_user_id = parse_widget_id(widget_id)
    if not auth_user_id:
        raise HTTPException(status_code=404, detail="Widget not found")

    config = await crud.get_config(db, WIDGET_CONFIG_KEY, user_id=auth_user_id)
    if not config or not config.get("enabled") or config.get("widget_id") != widget_id:
        raise HTTPException(status_code=404, detail="Widget not found")
    return auth_user_id, config


def _origin_host(origin: str) -> Optional[str]:
    try:
        return urlparse(origin).hostname
    except Exception:
        return None


@router.post("/widget/bootstrap")
@limiter.limit("10/minute")
async def widget_bootstrap(
    request: Request,
    payload: WidgetBootstrapRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create or resume an anonymous web session."""
    auth_user_id, config = await _load_widget_config(db, payload.widget_id)

    if not is_origin_allowed(payload.origin, config.get("allowed_origins", [])):
        raise HTTPException(status_code=403, detail="Origin not allowed")

    session_id = payload.session_id or secrets.token_urlsafe(18)
    session_identifier = f"web:{payload.widget_id}:{session_id}"
    user, _ = await crud.get_or_create_user(
        db=db,
        identifier=session_identifier,
        channel="web",
        auth_user_id=auth_user_id,
        defaults={
            "name": "Website visitor",
            "phone": None,
            "channel_user_id": session_identifier,
        },
    )

    token_payload = build_widget_session_payload(
        auth_user_id=auth_user_id,
        widget_id=payload.widget_id,
        session_id=session_id,
        origin=payload.origin,
        page_url=payload.page_url,
    )
    token = sign_widget_session(token_payload, config["widget_secret_hash"])
    history = await crud.get_user_messages(db, user.id, limit=20)

    return {
        "token": token,
        "session_id": session_id,
        "branding": {
            "primaryColor": config.get("default_primary_color", "#7C3AED"),
        },
        "conversation": {
            "user_id": user.id,
            "channel": "web",
            "origin_host": _origin_host(payload.origin),
            "messages": [
                {
                    "id": message.id,
                    "message_text": message.message_text,
                    "sender": message.sender,
                    "created_at": message.timestamp.isoformat() if message.timestamp else None,
                    "metadata": message.message_metadata,
                }
                for message in history
            ],
        },
    }


@router.post("/widget/message")
@limiter.limit("30/minute")
async def widget_message(
    request: Request,
    payload: WidgetMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Process a public message from an embedded web widget."""
    try:
        token_payload_raw = payload.token.split(".", 1)[0]
        padding = "=" * (-len(token_payload_raw) % 4)
        decoded = base64.urlsafe_b64decode(f"{token_payload_raw}{padding}")
        unverified_widget_id = json.loads(decoded.decode("utf-8")).get("widget_id")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid widget token") from exc

    auth_user_id, config = await _load_widget_config(db, unverified_widget_id)
    try:
        token_payload = verify_widget_session(payload.token, config["widget_secret_hash"])
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    session_identifier = f"web:{token_payload['widget_id']}:{token_payload['session_id']}"
    metadata = {
        "widget_id": token_payload["widget_id"],
        "session_id": token_payload["session_id"],
        "origin": token_payload["origin"],
        "page_url": payload.page_url,
        "user_agent": request.headers.get("user-agent"),
    }
    result = await process_incoming_message(
        db=db,
        auth_user_id=auth_user_id,
        identifier=session_identifier,
        channel="web",
        message=payload.message,
        user_defaults={
            "name": "Website visitor",
            "phone": None,
            "channel_user_id": session_identifier,
        },
        inbound_metadata=metadata,
        outbound_metadata=metadata,
    )

    return {
        "response": result["response"],
        "conversation_mode": result["conversation_mode"],
        "user_id": result["user_id"],
        "channel": "web",
    }


@router.get("/widget.js", response_class=PlainTextResponse, include_in_schema=False)
async def widget_script():
    """Return the embeddable widget loader script."""
    frontend_url = _frontend_url().rstrip("/")
    script = f"""
(function () {{
  var config = window.WhatsAppSalesBotConfig || {{}};
  if (!config.widgetId) {{
    console.error("WhatsAppSalesBotConfig.widgetId is required");
    return;
  }}

  var currentScript = document.currentScript;
  var apiBase = currentScript ? new URL(currentScript.src).origin : window.location.origin;
  var primaryColor = config.primaryColor || "#7C3AED";
  var iframe = document.createElement("iframe");
  var launcher = document.createElement("button");
  var open = false;

  function applyFrameLayout() {{
    var mobile = window.innerWidth <= 640;
    iframe.style.position = "fixed";
    iframe.style.right = mobile ? "12px" : "24px";
    iframe.style.bottom = mobile ? "72px" : "96px";
    iframe.style.width = mobile ? "calc(100vw - 24px)" : "380px";
    iframe.style.height = mobile ? "calc(100vh - 96px)" : "640px";
    iframe.style.maxWidth = "calc(100vw - 24px)";
    iframe.style.maxHeight = "calc(100vh - 96px)";
  }}

  launcher.type = "button";
  launcher.setAttribute("aria-label", "Open chat");
  launcher.style.position = "fixed";
  launcher.style.right = "24px";
  launcher.style.bottom = "24px";
  launcher.style.width = "56px";
  launcher.style.height = "56px";
  launcher.style.borderRadius = "999px";
  launcher.style.border = "0";
  launcher.style.cursor = "pointer";
  launcher.style.boxShadow = "0 18px 45px rgba(15, 23, 42, 0.28)";
  launcher.style.background = primaryColor;
  launcher.style.color = "#fff";
  launcher.style.fontSize = "24px";
  launcher.style.zIndex = "2147483000";
  launcher.innerHTML = "&#128172;";

  iframe.src = "{frontend_url}/widget?widgetId=" + encodeURIComponent(config.widgetId) +
    "&primaryColor=" + encodeURIComponent(primaryColor) +
    "&apiBase=" + encodeURIComponent(apiBase) +
    "&pageUrl=" + encodeURIComponent(window.location.href);
  iframe.title = "Chat widget";
  iframe.style.display = "none";
  iframe.style.border = "0";
  iframe.style.borderRadius = "20px";
  iframe.style.background = "#fff";
  iframe.style.boxShadow = "0 24px 80px rgba(15, 23, 42, 0.24)";
  iframe.style.zIndex = "2147482999";
  iframe.allow = "clipboard-write";
  applyFrameLayout();

  launcher.addEventListener("click", function () {{
    open = !open;
    iframe.style.display = open ? "block" : "none";
  }});

  window.addEventListener("resize", applyFrameLayout);
  window.addEventListener("message", function (event) {{
    if (event.data && event.data.type === "wa-sales-bot-close") {{
      open = false;
      iframe.style.display = "none";
    }}
  }});

  document.body.appendChild(iframe);
  document.body.appendChild(launcher);
}})();
""".strip()
    return PlainTextResponse(script, media_type="application/javascript")
