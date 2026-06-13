from fastapi import APIRouter, Depends

from routers.chat import verify_api_key


router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
async def list_models(_: None = Depends(verify_api_key)) -> dict:
    models = [
        {"id": "officina-primary", "object": "model", "owned_by": "officina"},
        {"id": "officina-plus", "object": "model", "owned_by": "officina"},
        {"id": "officina-secondary", "object": "model", "owned_by": "officina"},
        {"id": "officina-embeddings", "object": "model", "owned_by": "officina"},
        {"id": "officina-reasoning", "object": "model", "owned_by": "officina"},
        {"id": "officina-coding", "object": "model", "owned_by": "officina"},
    ]
    return {"object": "list", "data": models}
