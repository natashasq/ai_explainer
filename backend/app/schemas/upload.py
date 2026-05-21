from pydantic import BaseModel


class UploadResponse(BaseModel):
    knowledge_base_id: str
    filename: str
    chunk_count: int
