MAX_CHARS = 500
MIN_CHARS = 150


def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines = [line for line in lines if line]
    return "\n".join(cleaned_lines)


def split_into_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n") if p.strip()]


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

            # A single paragraph longer than max_chars gets hard-split
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

    # Merge chunks that are too small into the previous one if it fits
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


def chunk_text(text: str, max_chars: int = MAX_CHARS, min_chars: int = MIN_CHARS) -> list[str]:
    """Full pipeline: raw text -> list of chunk strings. Expects normalized text."""
    paragraphs = split_into_paragraphs(text)
    return chunk_paragraphs(paragraphs, max_chars=max_chars, min_chars=min_chars)
