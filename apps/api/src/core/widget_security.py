"""Helpers for widget configuration, origin validation, and signed session tokens."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any, Dict, Iterable, Optional
from urllib.parse import urlparse


WIDGET_CONFIG_KEY = "web_widget"
WIDGET_TOKEN_TTL_SECONDS = 60 * 60


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")


def normalize_origin(origin: str) -> str:
    """Normalize an origin value to scheme://host[:port]."""
    parsed = urlparse(origin.strip())
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Invalid origin")
    return f"{parsed.scheme}://{parsed.netloc}".lower()


def normalize_allowed_origins(origins: Iterable[str]) -> list[str]:
    """Normalize configured origins and drop empty values."""
    normalized: list[str] = []
    for origin in origins:
        value = str(origin).strip()
        if not value:
            continue
        normalized.append(normalize_origin(value))
    return sorted(set(normalized))


def is_origin_allowed(origin: str, allowed_origins: Iterable[str]) -> bool:
    """Check whether the request origin is explicitly allow-listed."""
    try:
        normalized_origin = normalize_origin(origin)
    except ValueError:
        return False
    return normalized_origin in normalize_allowed_origins(allowed_origins)


def make_widget_id(auth_user_id: str) -> str:
    """Create a stable public widget id from the tenant user id."""
    return f"ww_{_b64url_encode(auth_user_id.encode('utf-8'))}"


def parse_widget_id(widget_id: str) -> Optional[str]:
    """Resolve a tenant user id from a public widget id."""
    if not widget_id.startswith("ww_"):
        return None
    try:
        return _b64url_decode(widget_id[3:]).decode("utf-8")
    except Exception:
        return None


def generate_widget_secret() -> str:
    """Generate a new widget secret."""
    return secrets.token_urlsafe(32)


def hash_widget_secret(secret: str) -> str:
    """Hash a widget secret for storage."""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def sanitize_color(value: Optional[str], fallback: str = "#7C3AED") -> str:
    """Accept only simple hex colors for widget branding."""
    if not value:
        return fallback
    candidate = value.strip()
    if len(candidate) == 7 and candidate.startswith("#"):
        hex_part = candidate[1:]
        if all(char in "0123456789abcdefABCDEF" for char in hex_part):
            return candidate.upper()
    return fallback


def widget_token_signing_key(widget_secret_hash: str) -> bytes:
    """Derive the HMAC signing key for widget session tokens."""
    app_secret = os.getenv("WIDGET_SIGNING_SECRET") or os.getenv("SECRET_KEY") or "dev-widget-secret"
    return f"{app_secret}:{widget_secret_hash}".encode("utf-8")


def sign_widget_session(payload: Dict[str, Any], widget_secret_hash: str) -> str:
    """Create a signed session token for the widget."""
    serialized = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    encoded_payload = _b64url_encode(serialized)
    signature = hmac.new(
        widget_token_signing_key(widget_secret_hash),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_payload}.{_b64url_encode(signature)}"


def verify_widget_session(token: str, widget_secret_hash: str) -> Dict[str, Any]:
    """Verify a signed widget token and return its payload."""
    try:
        encoded_payload, encoded_signature = token.split(".", 1)
    except ValueError as exc:
        raise ValueError("Invalid token format") from exc

    expected_signature = hmac.new(
        widget_token_signing_key(widget_secret_hash),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    provided_signature = _b64url_decode(encoded_signature)

    if not hmac.compare_digest(expected_signature, provided_signature):
        raise ValueError("Invalid token signature")

    payload = json.loads(_b64url_decode(encoded_payload).decode("utf-8"))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("Token expired")
    return payload


def build_widget_config(auth_user_id: str, existing: Optional[Dict[str, Any]] = None) -> tuple[Dict[str, Any], Optional[str]]:
    """Ensure a tenant has a complete widget config. Returns config and optional fresh secret."""
    current = dict(existing or {})
    fresh_secret: Optional[str] = None

    if not current.get("widget_id"):
        current["widget_id"] = make_widget_id(auth_user_id)

    if not current.get("widget_secret_hash"):
        fresh_secret = generate_widget_secret()
        current["widget_secret_hash"] = hash_widget_secret(fresh_secret)

    current["enabled"] = bool(current.get("enabled", False))
    current["allowed_origins"] = normalize_allowed_origins(current.get("allowed_origins", []))
    current["default_primary_color"] = sanitize_color(current.get("default_primary_color"))
    return current, fresh_secret


def build_widget_session_payload(
    *,
    auth_user_id: str,
    widget_id: str,
    session_id: str,
    origin: str,
    page_url: str,
) -> Dict[str, Any]:
    """Build the payload used for widget session tokens."""
    now = int(time.time())
    return {
        "sub": auth_user_id,
        "widget_id": widget_id,
        "session_id": session_id,
        "origin": normalize_origin(origin),
        "page_url": page_url,
        "iat": now,
        "exp": now + WIDGET_TOKEN_TTL_SECONDS,
    }
