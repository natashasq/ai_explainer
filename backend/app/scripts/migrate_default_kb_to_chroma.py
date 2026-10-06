"""
One-off script: loads the default KB from JSON and inserts it into Chroma.
Run once from the backend/ directory:
    .venv/bin/python -m app.scripts.migrate_default_kb_to_chroma
"""
import json
from pathlib import Path

from app.services.chroma_store import add_chunks, collection_exists

DEFAULT_EMBEDDINGS_FILE = Path(__file__).resolve().parents[2] / "knowledge_base/processed/embeddings.json"


def main() -> None:
    if collection_exists("default"):
        print("Default KB already exists in Chroma — nothing to do.")
        return

    if not DEFAULT_EMBEDDINGS_FILE.exists():
        print(f"File not found: {DEFAULT_EMBEDDINGS_FILE}")
        return

    chunks = json.loads(DEFAULT_EMBEDDINGS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(chunks)} chunks from JSON.")

    add_chunks("default", chunks)
    print("Done — default KB is now in Chroma.")


if __name__ == "__main__":
    main()
