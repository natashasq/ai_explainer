import json
import math
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

EMBEDDINGS_FILE = Path("knowledge_base/processed/embeddings.json")
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


@lru_cache(maxsize=1)
def load_embedded_chunks() -> list[dict]:
    if not EMBEDDINGS_FILE.exists():
        raise FileNotFoundError(
            f"Embeddings file not found: {EMBEDDINGS_FILE}")

    with EMBEDDINGS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("embeddings.json must contain a list")

    return data


def get_query_embedding(query: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    return response.data[0].embedding


def retrieve_relevant_chunks(query: str, top_k: int = 3, min_score: float = 0.35) -> list[dict]:
    embedded_chunks = load_embedded_chunks()
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

    print("\nTop retrieved chunks:")
    for chunk in top_chunks:
        print(f'{chunk["source"]} | score={chunk["score"]:.4f}')

    relevant_chunks = [
        chunk for chunk in top_chunks if chunk["score"] >= min_score]

    return relevant_chunks


def build_context_block(chunks: list[dict]) -> str:
    parts: list[str] = []

    for chunk in chunks:
        parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")

    return "\n\n".join(parts)
