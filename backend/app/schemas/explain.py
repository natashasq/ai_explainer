from pydantic import BaseModel, Field
from typing import Literal


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class ExplainRequest(BaseModel):
    messages: list[ChatMessage]
    knowledge_base_id: str = "default"


class SourceItem(BaseModel):
    source: str
    text: str


class ExplainResponse(BaseModel):
    answer: str
    suggested_questions: list[str]
    sources: list[SourceItem]
