from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.explain import ExplainRequest, ExplainResponse
from app.services.llm_service import explain_from_messages, stream_answer_from_messages
from app.services.chroma_store import collection_exists

router = APIRouter(prefix="/api", tags=["explain"])


@router.post("/explain", response_model=ExplainResponse)
def explain(request: ExplainRequest):
    if not collection_exists(request.knowledge_base_id):
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge base not found: {request.knowledge_base_id}",
        )

    try:
        result = explain_from_messages(
            request.messages,
            request.knowledge_base_id,
        )
        return ExplainResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Unexpected server error") from exc


@router.post("/explain-stream")
def explain_stream(request: ExplainRequest):
    if not collection_exists(request.knowledge_base_id):
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge base not found: {request.knowledge_base_id}",
        )

    generator = stream_answer_from_messages(
        request.messages,
        request.knowledge_base_id,
    )
    return StreamingResponse(generator, media_type="text/plain; charset=utf-8")
