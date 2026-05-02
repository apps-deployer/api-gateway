from fastapi import APIRouter, Depends, Request

from src.auth import generate_service_token, get_current_user, require_service
from src.http_proxy import call_json, proxy_request
from src.schemas import CreateDeploymentRequest

router = APIRouter(tags=["proxy"])
internal_router = APIRouter(prefix="/internal", tags=["internal-proxy"])


def _settings():
    from src.main import settings
    return settings


@router.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_auth(path: str, request: Request):
    return await proxy_request(request, _settings().upstream.auth_service_url, f"/api/v1/auth/{path}")


@router.api_route("/api/v1/deployments", methods=["GET", "POST"])
@router.api_route("/api/v1/deployments/{path:path}", methods=["GET", "POST"])
async def proxy_deployments(request: Request, path: str = "", _user=Depends(get_current_user)):
    return await proxy_request(
        request,
        _settings().upstream.deployments_service_url,
        f"/api/v1/deployments/{path}" if path else "/api/v1/deployments",
    )


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
