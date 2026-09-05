"""
Generic passthrough proxy: forwards /api/v1/{segment}/... to the microservice
that owns that resource, preserving method, query string, body, and the
Authorization header. The owning service is the source of truth for auth
(role checks) and validation — the gateway does not re-implement either.

Adding a new resource to a service requires exactly one line here: map the
resource's first path segment to that service's base URL.
"""
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, Response

from app.core.config import settings

router = APIRouter(prefix="/api/v1", tags=["Proxy"])

# First path segment -> upstream service base URL.
SERVICE_ROUTES: dict[str, str] = {
    "employees": settings.HR_SERVICE_URL,
    "departments": settings.HR_SERVICE_URL,
    "schedules": settings.HR_SERVICE_URL,
    "working-schedules": settings.HR_SERVICE_URL,
    "contracts": settings.HR_SERVICE_URL,
    "job-positions": settings.HR_SERVICE_URL,
    "attendance": settings.ATTENDANCE_SERVICE_URL,
    "time-off": settings.ATTENDANCE_SERVICE_URL,
}

# Headers that must not be forwarded verbatim (hop-by-hop / recomputed by httpx).
_EXCLUDED_REQUEST_HEADERS = {"host", "content-length", "connection"}
_EXCLUDED_RESPONSE_HEADERS = {"content-length", "connection", "transfer-encoding"}

_client: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client


@router.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
)
async def proxy(full_path: str, request: Request) -> Response:
    segment = full_path.split("/", 1)[0]
    base_url = SERVICE_ROUTES.get(segment)
    if base_url is None:
        raise HTTPException(status_code=404, detail=f"No service registered for '/{segment}'")

    upstream_url = f"{base_url}/api/v1/{full_path}"
    body = await request.body()
    forward_headers = {
        k: v for k, v in request.headers.items() if k.lower() not in _EXCLUDED_REQUEST_HEADERS
    }

    client = _get_client()
    try:
        upstream_response = await client.request(
            request.method,
            upstream_url,
            params=request.query_params,
            content=body,
            headers=forward_headers,
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream service unreachable: {exc}") from exc

    response_headers = {
        k: v
        for k, v in upstream_response.headers.items()
        if k.lower() not in _EXCLUDED_RESPONSE_HEADERS
    }
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )
