import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: str
    name: str
    repo_url: str
    owner_id: str


class ProjectsListResponse(BaseModel):
    items: list[ProjectResponse]


class CreateProjectRequest(BaseModel):
    name: str
    repo_url: str
    framework_id: str = ""


class UpdateProjectRequest(BaseModel):
    name: str
    repo_url: str


class EnvResponse(BaseModel):
    id: str
    name: str
    project_id: str
    target_branch: str


class EnvsListResponse(BaseModel):
    items: list[EnvResponse]


class CreateEnvRequest(BaseModel):
    name: str
    target_branch: str


class UpdateEnvRequest(BaseModel):
    name: str
    target_branch: str


class VarResponse(BaseModel):
    id: str
    key: str


class VarsListResponse(BaseModel):
    items: list[VarResponse]


class CreateVarRequest(BaseModel):
    key: str
    value: str


class UpdateVarRequest(BaseModel):
    value: str


class DeployConfigResponse(BaseModel):
    id: str
    project_id: str
    framework_id: str
    root_dir_override: str
    output_dir_override: str
    base_image_override: str
    install_cmd_override: str
    build_cmd_override: str
    run_cmd_override: str


class UpdateDeployConfigRequest(BaseModel):
    framework_id: str = ""
    root_dir_override: str = ""
    output_dir_override: str = ""
    base_image_override: str = ""
    install_cmd_override: str = ""
    build_cmd_override: str = ""
    run_cmd_override: str = ""


class FrameworkResponse(BaseModel):
    id: str
    name: str
    root_dir: str
    output_dir: str
    base_image: str
    install_cmd: str
    build_cmd: str
    run_cmd: str


class FrameworksListResponse(BaseModel):
    items: list[FrameworkResponse]


class TriggerType(StrEnum):
    MANUAL = "manual"
    WEBHOOK = "webhook"


class CreateDeploymentRequest(BaseModel):
    project_id: uuid.UUID
    env_id: uuid.UUID
    commit_sha: str | None = None
    commit_message: str | None = None
    trigger_type: TriggerType = TriggerType.MANUAL


class JobResponse(BaseModel):
    id: uuid.UUID
    type: str
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    error: str | None
    created_at: datetime


class ArtifactResponse(BaseModel):
    id: uuid.UUID
    image: str
    url: str | None = None
    created_at: datetime


class DeploymentRunResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    env_id: uuid.UUID
    status: str
    trigger_type: str
    commit_sha: str | None
    commit_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime
    jobs: list[JobResponse] = []
    artifact: ArtifactResponse | None = None


class DeploymentRunListResponse(BaseModel):
    items: list[DeploymentRunResponse]
    total: int


class GitEnvLookupRequest(BaseModel):
    repo_url: str
    target_branch: str


class InstallationUpsertRequest(BaseModel):
    installation_id: int
    github_account_id: int
    github_account_login: str
    sender_github_id: int | None = None


class InstallationStatusResponse(BaseModel):
    installed: bool
    install_url: str
