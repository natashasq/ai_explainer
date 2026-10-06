import chromadb
from chromadb.api import ClientAPI
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = _BASE_DIR / "knowledge_base/chroma"

_client: ClientAPI | None = None


def _get_client() -> ClientAPI:
    global _client
    if _client is None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client


def collection_exists(knowledge_base_id: str) -> bool:
    try:
        _get_client().get_collection(name=knowledge_base_id)
        return True
    except Exception:
        return False


def add_chunks(knowledge_base_id: str, chunks: list[dict]) -> None:
    collection = _get_client().get_or_create_collection(
        name=knowledge_base_id,
        metadata={"hnsw:space": "cosine"},
    )
    collection.add(
        ids=[c["id"] for c in chunks],
        embeddings=[c["embedding"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"]} for c in chunks],
    )


def query_chunks(
    knowledge_base_id: str,
    query_embedding: list[float],
    top_k: int = 3,
    min_score: float = 0.35,
) -> list[dict]:
    try:
        collection = _get_client().get_collection(name=knowledge_base_id)
    except Exception:
        return []

    n_results = min(top_k, collection.count())
    if n_results == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    chunks = []
    for id_, text, metadata, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        score = 1.0 - distance  # cosine space: distance = 1 - similarity
        print(f"[Chroma] score={score:.3f} | {metadata['source']} | {text[:60]}...")
        if score >= min_score:
            chunks.append({
                "id": id_,
                "source": metadata["source"],
                "text": text,
                "score": score,
            })

    return chunks