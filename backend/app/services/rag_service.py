import json
import math
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_EMBEDDINGS_FILE = Path("knowledge_base/processed/embeddings.json")
UPLOAD_PROCESSED_DIR = Path("knowledge_base/uploads/processed")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Embedding vectors must have the same length")

    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def load_embedded_chunks_for_kb(knowledge_base_id: str) -> list[dict]:
    if knowledge_base_id == "default":
        path = DEFAULT_EMBEDDINGS_FILE
    else:
        path = UPLOAD_PROCESSED_DIR / f"{knowledge_base_id}.json"

    if not path.exists():
        raise FileNotFoundError(
            f"Knowledge base embeddings not found for: {knowledge_base_id}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Knowledge base embeddings file must contain a list")

    return data


def get_query_embedding(query: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    return response.data[0].embedding


def retrieve_relevant_chunks(
    query: str,
    knowledge_base_id: str,
    top_k: int = 3,
    min_score: float = 0.35,
) -> list[dict]:
    embedded_chunks = load_embedded_chunks_for_kb(knowledge_base_id)
    query_embedding = get_query_embedding(query)

    scored_chunks: list[dict] = []

    for chunk in embedded_chunks:
        score = cosine_similarity(query_embedding, chunk["embedding"])
        scored_chunks.append(
            {
                "id": chunk["id"],
                "source": chunk["source"],
                "text": chunk["text"],
                "score": score,
            }
        )

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)
    top_chunks = scored_chunks[:top_k]

    relevant_chunks = [
        chunk for chunk in top_chunks if chunk["score"] >= min_score]
    return relevant_chunks


def build_context_block(chunks: list[dict]) -> str:
    parts: list[str] = []

    for chunk in chunks:
        parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")

    return "\n\n".join(parts)
