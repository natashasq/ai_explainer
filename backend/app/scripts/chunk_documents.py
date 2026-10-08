import json
from pathlib import Path

from app.services.chunking import chunk_text, normalize_text


RAW_DIR = Path("knowledge_base/raw")
OUTPUT_FILE = Path("knowledge_base/processed/chunks.json")


def build_chunks() -> list[dict]:
    all_chunks: list[dict] = []

    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"Raw knowledge base directory not found: {RAW_DIR}")

    txt_files = sorted(RAW_DIR.glob("*.txt"))

    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in {RAW_DIR}")

    for file_path in txt_files:
        raw_text = file_path.read_text(encoding="utf-8")
        normalized = normalize_text(raw_text)
        chunks = chunk_text(normalized)

        source_name = file_path.name
        source_stem = file_path.stem

        for index, chunk in enumerate(chunks):
            all_chunks.append(
                {
                    "id": f"{source_stem}_{index}",
                    "source": source_name,
                    "text": chunk,
                }
            )

    return all_chunks


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    chunks = build_chunks()

    OUTPUT_FILE.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Saved {len(chunks)} chunks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
