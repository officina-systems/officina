import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import admin
from routers import chat
from routers import embeddings
from routers import debug
from routers import workspaces
from routers import folders
from routers import conversations
from routers import models
from routers import documents

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="OFFICINA API",
    version="0.2.0",
    description="T1 PUSH pipeline + API operativa + admin Docker",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restringir en produccion
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(chat.router)
app.include_router(embeddings.router)
app.include_router(debug.router)
app.include_router(workspaces.router)
app.include_router(folders.router)
app.include_router(conversations.router)
app.include_router(models.router)
app.include_router(documents.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "officina-fastapi", "version": "0.2.0"}
