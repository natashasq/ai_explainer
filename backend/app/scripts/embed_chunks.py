import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CHUNKS_FILE = Path("knowledge_base/processed/chunks.json")
OUTPUT_FILE = Path("knowledge_base/processed/embeddings.json")

# Promeni model ovde ako želiš kasnije.
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_chunks() -> list[dict]:
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(f"Chunks file not found: {CHUNKS_FILE}")

    with CHUNKS_FILE.open("r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not isinstance(chunks, list):
        raise ValueError("chunks.json must contain a list")

    return chunks


def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def build_embeddings(chunks: list[dict]) -> list[dict]:
    embedded_chunks: list[dict] = []

    total = len(chunks)

    for index, chunk in enumerate(chunks, start=1):
        chunk_id = chunk["id"]
        source = chunk["source"]
        text = chunk["text"]

        print(f"[{index}/{total}] Embedding {chunk_id} from {source}")

        embedding = get_embedding(text)

        embedded_chunks.append(
            {
                "id": chunk_id,
                "source": source,
                "text": text,
                "embedding": embedding,
            }
        )

    return embedded_chunks


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is not set")

    chunks = load_chunks()
    embedded_chunks = build_embeddings(chunks)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(embedded_chunks, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(embedded_chunks)} embedded chunks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
