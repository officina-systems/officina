import docker
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader

from config import settings

router = APIRouter(prefix="/admin", tags=["admin"])

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def verify_key(key: str = Depends(api_key_header)) -> None:
    if key != settings.FASTAPI_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


def get_docker_client() -> docker.DockerClient:
    try:
        return docker.from_env()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Docker socket unavailable: {e}")


@router.get("/health", dependencies=[Depends(verify_key)])
async def admin_health():
    client = get_docker_client()
    containers = {
        c.name: c.status
        for c in client.containers.list(all=True)
        if c.name.startswith("officina-")
    }
    return {"status": "ok", "containers": containers}


@router.get("/services", dependencies=[Depends(verify_key)])
async def list_services():
    client = get_docker_client()
    return [
        {"name": c.name, "status": c.status, "image": c.image.tags}
        for c in client.containers.list(all=True)
        if c.name.startswith("officina-")
    ]


@router.post("/services/{name}/restart", dependencies=[Depends(verify_key)])
async def restart_service(name: str):
    client = get_docker_client()
    try:
        container = client.containers.get(f"officina-{name}")
        container.restart()
        return {"status": "restarted", "service": f"officina-{name}"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=f"Service '{name}' not found")


@router.get("/logs/{name}", dependencies=[Depends(verify_key)])
async def get_logs(name: str, lines: int = 100):
    client = get_docker_client()
    try:
        container = client.containers.get(f"officina-{name}")
        logs = container.logs(tail=lines).decode("utf-8", errors="replace")
        return {"service": f"officina-{name}", "logs": logs}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=f"Service '{name}' not found")
