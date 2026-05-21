import json
from pathlib import Path


RAW_DIR = Path("knowledge_base/raw")
OUTPUT_FILE = Path("knowledge_base/processed/chunks.json")

MAX_CHARS = 500
MIN_CHARS = 150


def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines = [line for line in lines if line]
    return "\n".join(cleaned_lines)


def split_into_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    return paragraphs


def chunk_paragraphs(paragraphs: list[str], max_chars: int, min_chars: int) -> list[str]:
    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        candidate = f"{current_chunk}\n{paragraph}".strip(
        ) if current_chunk else paragraph

        if len(candidate) <= max_chars:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            # Ako je jedan paragraf sam predugačak, iseći ga grubo
            if len(paragraph) > max_chars:
                start = 0
                while start < len(paragraph):
                    piece = paragraph[start:start + max_chars].strip()
                    if piece:
                        chunks.append(piece)
                    start += max_chars
                current_chunk = ""
            else:
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    # Spoji premale chunkove sa prethodnim ako može
    merged_chunks: list[str] = []

    for chunk in chunks:
        if (
            merged_chunks
            and len(chunk) < min_chars
            and len(merged_chunks[-1]) + 1 + len(chunk) <= max_chars
        ):
            merged_chunks[-1] = f"{merged_chunks[-1]}\n{chunk}".strip()
        else:
            merged_chunks.append(chunk)

    return merged_chunks


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
        paragraphs = split_into_paragraphs(normalized)
        chunks = chunk_paragraphs(
            paragraphs, max_chars=MAX_CHARS, min_chars=MIN_CHARS)

        source_name = file_path.name
        source_stem = file_path.stem

        for index, chunk_text in enumerate(chunks):
            all_chunks.append(
                {
                    "id": f"{source_stem}_{index}",
                    "source": source_name,
                    "text": chunk_text,
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
