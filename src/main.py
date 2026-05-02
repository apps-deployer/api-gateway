from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import load_settings
from src.grpc_client import ProjectsGrpcClient

settings = load_settings()
grpc_client = ProjectsGrpcClient(settings.grpc.projects_service_addr)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await grpc_client.close()


app = FastAPI(title="API Gateway", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.server.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


from src.api.projects import internal_router as internal_projects_router
from src.api.projects import router as projects_router
from src.api.proxy import internal_router as internal_proxy_router
from src.api.proxy import router as proxy_router

app.include_router(proxy_router)
app.include_router(projects_router)
app.include_router(internal_proxy_router)
app.include_router(internal_projects_router)
