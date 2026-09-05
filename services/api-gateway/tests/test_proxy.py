from unittest.mock import AsyncMock

import httpx
import pytest

import app.proxy.router as proxy_router


class _FakeAsyncClient:
    def __init__(self, response: httpx.Response):
        self._response = response
        self.request = AsyncMock(return_value=response)


@pytest.mark.asyncio
async def test_proxy_forwards_to_registered_service(client, monkeypatch):
    upstream_response = httpx.Response(
        200,
        json=[{"id": "abc", "first_name": "Ada"}],
        headers={"content-type": "application/json"},
    )
    fake_client = _FakeAsyncClient(upstream_response)
    monkeypatch.setattr(proxy_router, "_get_client", lambda: fake_client)

    response = await client.get(
        "/api/v1/employees/",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json() == [{"id": "abc", "first_name": "Ada"}]

    called_args, called_kwargs = fake_client.request.call_args
    assert called_args[0] == "GET"
    assert called_args[1] == f"{proxy_router.settings.HR_SERVICE_URL}/api/v1/employees/"
    assert called_kwargs["headers"]["authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_proxy_rejects_unregistered_segment(client):
    response = await client.get("/api/v1/nonexistent-resource/")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_proxy_returns_502_on_upstream_unreachable(client, monkeypatch):
    fake_client = AsyncMock()
    fake_client.request = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
    monkeypatch.setattr(proxy_router, "_get_client", lambda: fake_client)

    response = await client.get("/api/v1/employees/")
    assert response.status_code == 502
