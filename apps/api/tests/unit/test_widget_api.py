"""Tests for the public web widget API."""

from fastapi.testclient import TestClient


class TestWidgetAPI:
    """Validate widget bootstrap, security, and message persistence."""

    def test_widget_bootstrap_rejects_disallowed_origin(self, client: TestClient, auth_headers: dict[str, str]):
        client.put(
            "/integrations/web-widget",
            headers=auth_headers,
            json={
                "enabled": True,
                "allowed_origins": ["https://allowed.example"],
                "default_primary_color": "#0F766E",
            },
        )
        config = client.get("/integrations/web-widget", headers=auth_headers).json()

        response = client.post(
            "/widget/bootstrap",
            json={
                "widget_id": config["widget_id"],
                "origin": "https://evil.example",
                "page_url": "https://evil.example/page",
            },
        )

        assert response.status_code == 403

    def test_widget_bootstrap_and_message_flow(self, client: TestClient, auth_headers: dict[str, str]):
        client.put(
            "/integrations/web-widget",
            headers=auth_headers,
            json={
                "enabled": True,
                "allowed_origins": ["https://allowed.example"],
                "default_primary_color": "#1D4ED8",
            },
        )
        config = client.get("/integrations/web-widget", headers=auth_headers).json()

        bootstrap = client.post(
            "/widget/bootstrap",
            json={
                "widget_id": config["widget_id"],
                "origin": "https://allowed.example",
                "page_url": "https://allowed.example/pricing",
            },
        )

        assert bootstrap.status_code == 200, bootstrap.text
        bootstrap_data = bootstrap.json()
        assert bootstrap_data["branding"]["primaryColor"] == "#1D4ED8"
        assert bootstrap_data["conversation"]["channel"] == "web"
        assert bootstrap_data["session_id"]
        assert bootstrap_data["token"]

        message_response = client.post(
            "/widget/message",
            json={
                "token": bootstrap_data["token"],
                "message": "Hola desde el sitio web",
                "page_url": "https://allowed.example/pricing",
            },
        )

        assert message_response.status_code == 200, message_response.text
        message_data = message_response.json()
        assert message_data["channel"] == "web"
        assert message_data["response"]

        conversations = client.get("/conversations", headers=auth_headers)
        assert conversations.status_code == 200
        payload = conversations.json()
        assert any(item.get("channel") == "web" for item in payload)

    def test_widget_message_rejects_invalid_token(self, client: TestClient):
        response = client.post(
            "/widget/message",
            json={
                "token": "invalid.token",
                "message": "Hola",
                "page_url": "https://allowed.example",
            },
        )

        assert response.status_code == 401
