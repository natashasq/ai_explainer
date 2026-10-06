import os

from dotenv import load_dotenv
from openai import OpenAI

from app.services.chroma_store import query_chunks as chroma_query_chunks

load_dotenv()

EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    query_embedding = get_query_embedding(query)
    return chroma_query_chunks(knowledge_base_id, query_embedding, top_k, min_score)


def build_context_block(chunks: list[dict]) -> str:
    parts: list[str] = []

    for chunk in chunks:
        parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")

    return "\n\n".join(parts)
