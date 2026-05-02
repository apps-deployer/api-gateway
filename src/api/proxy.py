from fastapi import APIRouter, Depends, Request

from src.auth import generate_service_token, get_current_user, require_service
from src.http_proxy import call_json, proxy_request
from src.schemas import CreateDeploymentRequest, InstallationStatusResponse, InstallationUpsertRequest

router = APIRouter(tags=["proxy"])
internal_router = APIRouter(prefix="/internal", tags=["internal-proxy"])


def _settings():
    from src.main import settings
    return settings


@router.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_auth(path: str, request: Request):
    return await proxy_request(request, _settings().upstream.auth_service_url, f"/api/v1/auth/{path}")


@router.get("/api/v1/github/installations/status", response_model=InstallationStatusResponse)
async def installation_status(user=Depends(get_current_user)):
    settings = _settings()
    headers = {"Authorization": f"Bearer {generate_service_token(settings.auth.jwt_secret)}"}
    return await call_json(
        "GET",
        settings.upstream.auth_service_url,
        "/internal/github/installations/status",
        headers={**headers, "X-User-Id": user.id},
    )


@router.api_route("/api/v1/deployments", methods=["GET", "POST"])
@router.api_route("/api/v1/deployments/{path:path}", methods=["GET", "POST"])
async def proxy_deployments(request: Request, path: str = "", _user=Depends(get_current_user)):
    return await proxy_request(
        request,
        _settings().upstream.deployments_service_url,
        f"/api/v1/deployments/{path}" if path else "/api/v1/deployments",
    )


@internal_router.post("/github/installations", status_code=204)
async def upsert_installation(body: InstallationUpsertRequest, _token: str = Depends(require_service)):
    settings = _settings()
    headers = {"Authorization": f"Bearer {generate_service_token(settings.auth.jwt_secret)}"}
    await call_json("PUT", settings.upstream.auth_service_url, "/internal/github/installations", json=body.model_dump(), headers=headers)


@internal_router.delete("/github/installations/{installation_id}", status_code=204)
async def delete_installation(installation_id: int, _token: str = Depends(require_service)):
    settings = _settings()
    headers = {"Authorization": f"Bearer {generate_service_token(settings.auth.jwt_secret)}"}
    await call_json("DELETE", settings.upstream.auth_service_url, f"/internal/github/installations/{installation_id}", headers=headers)


@internal_router.get("/github/installations/{installation_id}/exists")
async def installation_exists(installation_id: int, _token: str = Depends(require_service)):
    settings = _settings()
    headers = {"Authorization": f"Bearer {generate_service_token(settings.auth.jwt_secret)}"}
    return await call_json("GET", settings.upstream.auth_service_url, f"/internal/github/installations/{installation_id}/exists", headers=headers)


@internal_router.post("/deployments")
async def create_webhook_deployment(body: CreateDeploymentRequest, _token: str = Depends(require_service)):
    settings = _settings()
    headers = {"Authorization": f"Bearer {generate_service_token(settings.auth.jwt_secret)}"}
    return await call_json(
        "POST",
        settings.upstream.deployments_service_url,
        "/internal/deployments",
        json=body.model_dump(mode="json"),
        headers=headers,
    )
