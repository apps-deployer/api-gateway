from fastapi import APIRouter, Depends, HTTPException

import grpc
from src.auth import CurrentUser, get_current_user, require_service
from src.schemas import (
    CreateEnvRequest,
    CreateProjectRequest,
    CreateVarRequest,
    DeployConfigResponse,
    EnvResponse,
    EnvsListResponse,
    FrameworkResponse,
    FrameworksListResponse,
    GitEnvLookupRequest,
    ProjectResponse,
    ProjectsListResponse,
    UpdateDeployConfigRequest,
    UpdateEnvRequest,
    UpdateProjectRequest,
    UpdateVarRequest,
    VarResponse,
    VarsListResponse,
)

router = APIRouter(prefix="/api/v1", tags=["projects"])
internal_router = APIRouter(prefix="/internal/projects", tags=["internal-projects"])


def _grpc_error_to_http(e: grpc.RpcError):
    code = e.code()
    if code == grpc.StatusCode.NOT_FOUND:
        raise HTTPException(status_code=404, detail=e.details())
    if code == grpc.StatusCode.PERMISSION_DENIED:
        raise HTTPException(status_code=403, detail=e.details())
    if code == grpc.StatusCode.UNAUTHENTICATED:
        raise HTTPException(status_code=401, detail=e.details())
    if code == grpc.StatusCode.ALREADY_EXISTS:
        raise HTTPException(status_code=409, detail=e.details())
    if code == grpc.StatusCode.INVALID_ARGUMENT:
        raise HTTPException(status_code=422, detail=e.details())
    raise HTTPException(status_code=500, detail=e.details())


def _get_grpc():
    from src.main import grpc_client
    return grpc_client


def _as_http_error(e: Exception):
    if hasattr(e, "code"):
        _grpc_error_to_http(e)
    raise e


@router.get("/projects", response_model=ProjectsListResponse)
async def list_projects(user: CurrentUser = Depends(get_current_user)):
    try:
        projects = await _get_grpc().with_token(user.token).list_projects()
    except Exception as e:
        _as_http_error(e)
    return ProjectsListResponse(items=[ProjectResponse(**p.__dict__) for p in projects])


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(body: CreateProjectRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        project = await _get_grpc().with_token(user.token).create_project(
            name=body.name,
            repo_url=body.repo_url,
            deploy_config_template_id=body.framework_id,
        )
    except Exception as e:
        _as_http_error(e)
    return ProjectResponse(**project.__dict__)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        project = await _get_grpc().with_token(user.token).get_project(project_id)
    except Exception as e:
        _as_http_error(e)
    return ProjectResponse(**project.__dict__)


@router.put("/projects/{project_id}", status_code=204)
async def update_project(project_id: str, body: UpdateProjectRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        await _get_grpc().with_token(user.token).update_project(project_id, name=body.name, repo_url=body.repo_url)
    except Exception as e:
        _as_http_error(e)


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        await _get_grpc().with_token(user.token).delete_project(project_id)
    except Exception as e:
        _as_http_error(e)


@router.get("/projects/{project_id}/envs", response_model=EnvsListResponse)
async def list_envs(project_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        envs = await _get_grpc().with_token(user.token).list_envs(project_id)
    except Exception as e:
        _as_http_error(e)
    return EnvsListResponse(items=[EnvResponse(**e.__dict__) for e in envs])


@router.post("/projects/{project_id}/envs", response_model=EnvResponse, status_code=201)
async def create_env(project_id: str, body: CreateEnvRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        env = await _get_grpc().with_token(user.token).create_env(
            name=body.name, project_id=project_id, target_branch=body.target_branch
        )
    except Exception as e:
        _as_http_error(e)
    return EnvResponse(**env.__dict__)


@router.put("/envs/{env_id}", status_code=204)
async def update_env(env_id: str, body: UpdateEnvRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        await _get_grpc().with_token(user.token).update_env(env_id, name=body.name, target_branch=body.target_branch)
    except Exception as e:
        _as_http_error(e)


@router.delete("/envs/{env_id}", status_code=204)
async def delete_env(env_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        await _get_grpc().with_token(user.token).delete_env(env_id)
    except Exception as e:
        _as_http_error(e)


@router.get("/projects/{project_id}/vars", response_model=VarsListResponse)
async def list_project_vars(project_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        vars_ = await _get_grpc().with_token(user.token).list_project_vars(project_id)
    except Exception as e:
        _as_http_error(e)
    return VarsListResponse(items=[VarResponse(**v.__dict__) for v in vars_])


@router.post("/projects/{project_id}/vars", response_model=VarResponse, status_code=201)
async def create_project_var(project_id: str, body: CreateVarRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        var = await _get_grpc().with_token(user.token).create_project_var(
            project_id=project_id, key=body.key, value=body.value
        )
    except Exception as e:
        _as_http_error(e)
    return VarResponse(**var.__dict__)


@router.put("/vars/project/{var_id}", status_code=204)
async def update_project_var(var_id: str, body: UpdateVarRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        await _get_grpc().with_token(user.token).update_project_var(var_id, value=body.value)
    except Exception as e:
        _as_http_error(e)


@router.delete("/vars/project/{var_id}", status_code=204)
async def delete_project_var(var_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        await _get_grpc().with_token(user.token).delete_project_var(var_id)
    except Exception as e:
        _as_http_error(e)


@router.get("/envs/{env_id}/vars", response_model=VarsListResponse)
async def list_env_vars(env_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        vars_ = await _get_grpc().with_token(user.token).list_env_vars(env_id)
    except Exception as e:
        _as_http_error(e)
    return VarsListResponse(items=[VarResponse(**v.__dict__) for v in vars_])


@router.post("/envs/{env_id}/vars", response_model=VarResponse, status_code=201)
async def create_env_var(env_id: str, body: CreateVarRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        var = await _get_grpc().with_token(user.token).create_env_var(env_id=env_id, key=body.key, value=body.value)
    except Exception as e:
        _as_http_error(e)
    return VarResponse(**var.__dict__)


@router.put("/vars/env/{var_id}", status_code=204)
async def update_env_var(var_id: str, body: UpdateVarRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        await _get_grpc().with_token(user.token).update_env_var(var_id, value=body.value)
    except Exception as e:
        _as_http_error(e)


@router.delete("/vars/env/{var_id}", status_code=204)
async def delete_env_var(var_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        await _get_grpc().with_token(user.token).delete_env_var(var_id)
    except Exception as e:
        _as_http_error(e)


@router.get("/projects/{project_id}/deploy-config", response_model=DeployConfigResponse)
async def get_deploy_config(project_id: str, user: CurrentUser = Depends(get_current_user)):
    try:
        cfg = await _get_grpc().with_token(user.token).get_deploy_config(project_id)
    except Exception as e:
        _as_http_error(e)
    return DeployConfigResponse(**cfg.__dict__)


@router.put("/projects/{project_id}/deploy-config", status_code=204)
async def update_deploy_config(
    project_id: str, body: UpdateDeployConfigRequest, user: CurrentUser = Depends(get_current_user)
):
    grpc_client = _get_grpc().with_token(user.token)
    try:
        cfg = await grpc_client.get_deploy_config(project_id)
        await grpc_client.update_deploy_config(
            config_id=cfg.id,
            framework_id=body.framework_id,
            root_dir_override=body.root_dir_override,
            output_dir_override=body.output_dir_override,
            base_image_override=body.base_image_override,
            install_cmd_override=body.install_cmd_override,
            build_cmd_override=body.build_cmd_override,
            run_cmd_override=body.run_cmd_override,
        )
    except Exception as e:
        _as_http_error(e)


@router.get("/frameworks", response_model=FrameworksListResponse)
async def list_frameworks(user: CurrentUser = Depends(get_current_user)):
    try:
        frameworks = await _get_grpc().with_token(user.token).list_frameworks()
    except Exception as e:
        _as_http_error(e)
    return FrameworksListResponse(items=[FrameworkResponse(**f.__dict__) for f in frameworks])


@internal_router.post("/env-by-git", response_model=EnvResponse)
async def get_env_by_git(body: GitEnvLookupRequest, _token: str = Depends(require_service)):
    from src.main import settings
    from src.auth import generate_service_token

    try:
        env = await _get_grpc().with_token(
            generate_service_token(settings.auth.jwt_secret)
        ).get_env_by_git(body.repo_url, body.target_branch)
    except Exception as e:
        _as_http_error(e)
    return EnvResponse(**env.__dict__)
