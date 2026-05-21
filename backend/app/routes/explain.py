from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.explain import ExplainRequest, ExplainResponse
from app.services.llm_service import explain_from_messages, stream_answer_from_messages

router = APIRouter(prefix="/api", tags=["explain"])


@router.post("/explain", response_model=ExplainResponse)
def explain(request: ExplainRequest):
    try:
        result = explain_from_messages(request.messages)
        return ExplainResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Unexpected server error") from exc


@router.post("/explain-stream")
def explain_stream(request: ExplainRequest):
    generator = stream_answer_from_messages(request.messages)
    return StreamingResponse(generator, media_type="text/plain; charset=utf-8")
