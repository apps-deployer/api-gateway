import os
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8002
    frontend_url: str = "http://localhost:5173"


class AuthConfig(BaseModel):
    jwt_secret: str = "your_jwt_secret"


class GrpcConfig(BaseModel):
    projects_service_addr: str = "localhost:50051"


class UpstreamConfig(BaseModel):
    auth_service_url: str = "http://localhost:8001"
    deployments_service_url: str = "http://localhost:8000"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GATEWAY_", env_nested_delimiter="__")

    env: str = "local"
    server: ServerConfig = ServerConfig()
    auth: AuthConfig = AuthConfig()
    grpc: GrpcConfig = GrpcConfig()
    upstream: UpstreamConfig = UpstreamConfig()


def load_settings() -> Settings:
    config_path = os.environ.get("CONFIG_PATH")
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            data = yaml.safe_load(f)
        return Settings(**data)
    return Settings()
