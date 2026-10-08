import os
import re
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
from app.services.chroma_store import add_chunks
from app.services.chunking import chunk_text, normalize_text

load_dotenv()

_BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_RAW_DIR = _BASE_DIR / "knowledge_base/uploads/raw"
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def slugify_filename(filename: str) -> str:
    stem = Path(filename).stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    return stem or "document"


def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


async def process_uploaded_file(file: UploadFile, existing_kb_id: str | None = None) -> dict:
    filename = file.filename or "document"
    content = await file.read()

    if filename.lower().endswith(".pdf"):
        try:
            text = extract_text_from_pdf(content)
        except Exception as exc:
            raise ValueError("Could not extract text from PDF") from exc
    else:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("File must be valid UTF-8 text") from exc

    normalized = normalize_text(text)

    if len(normalized) < 30:
        raise ValueError("Uploaded file is too short")

    chunk_texts = chunk_text(normalized)

    if not chunk_texts:
        raise ValueError("Could not generate chunks from the uploaded file")

    knowledge_base_id = existing_kb_id if existing_kb_id and existing_kb_id != "default" else f"upload_{uuid4().hex[:8]}"
    safe_name = slugify_filename(filename)

    UPLOAD_RAW_DIR.mkdir(parents=True, exist_ok=True)

    raw_path = UPLOAD_RAW_DIR / f"{knowledge_base_id}_{safe_name}.txt"
    raw_path.write_text(normalized, encoding="utf-8")

    embedded_chunks: list[dict] = []

    for index, chunk in enumerate(chunk_texts):
        embedding = get_embedding(chunk)
        embedded_chunks.append(
            {
                "id": f"{knowledge_base_id}_{index}",
                "source": filename,
                "text": chunk,
                "embedding": embedding,
            }
        )

    add_chunks(knowledge_base_id, embedded_chunks)

    return {
        "knowledge_base_id": knowledge_base_id,
        "filename": filename,
        "chunk_count": len(embedded_chunks),
    }
