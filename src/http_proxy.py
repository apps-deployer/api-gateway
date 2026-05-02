from typing import Any

import httpx
from fastapi import HTTPException, Request, Response


async def proxy_request(
    request: Request,
    base_url: str,
    upstream_path: str,
    *,
    headers: dict[str, str] | None = None,
) -> Response:
    excluded = {"host", "content-length"}
    outgoing_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in excluded
    }
    if headers:
        outgoing_headers.update(headers)

    body = await request.body()
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0, follow_redirects=False) as client:
        resp = await client.request(
            request.method,
            upstream_path,
            params=request.query_params,
            content=body,
            headers=outgoing_headers,
        )
    response_headers = {
        k: v for k, v in resp.headers.items()
        if k.lower() not in {"content-encoding", "transfer-encoding", "connection"}
    }
    return Response(content=resp.content, status_code=resp.status_code, headers=response_headers)


async def call_json(
    method: str,
    base_url: str,
    path: str,
    *,
    json: Any | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        resp = await client.request(method, path, json=json, headers=headers)
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)
    if resp.status_code == 204 or not resp.content:
        return None
    return resp.json()
