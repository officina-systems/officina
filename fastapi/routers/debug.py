from fastapi import APIRouter, Depends
from pydantic import BaseModel

from routers.chat import verify_api_key
from pipeline.retrieval import retrieve
from pipeline.forma_c import clarify_task
from pipeline.prompt import assemble_prompt


router = APIRouter(prefix="/debug", tags=["debug"])


class RetrievalDebugRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    workspace_id: str | None = None
    folder_id: str | None = None


class FormaCDebugRequest(BaseModel):
    message: str


class PromptDebugRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    workspace_id: str | None = None
    folder_id: str | None = None


@router.post("/retrieval")
async def debug_retrieval(
    req: RetrievalDebugRequest,
    _: None = Depends(verify_api_key),
):
    return await retrieve(
        message=req.message,
        conversation_id=req.conversation_id,
        workspace_id=req.workspace_id,
        folder_id=req.folder_id,
    )


@router.post("/forma-c")
async def debug_forma_c(
    req: FormaCDebugRequest,
    _: None = Depends(verify_api_key),
):
    clarified = await clarify_task(req.message)
    return {
        "original": req.message,
        "clarified": clarified,
    }


@router.post("/prompt")
async def debug_prompt(
    req: PromptDebugRequest,
    _: None = Depends(verify_api_key),
):
    retrieval_result = await retrieve(
        message=req.message,
        conversation_id=req.conversation_id,
        workspace_id=req.workspace_id,
        folder_id=req.folder_id,
    )
    clarified = await clarify_task(req.message)
    messages = assemble_prompt(
        retrieval_result=retrieval_result,
        original_message=req.message,
        clarified_message=clarified,
    )
    return {
        "clarified": clarified,
        "messages": messages,
    }
