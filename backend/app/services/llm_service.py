import json
import os
from collections.abc import Generator

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.explain import ChatMessage
from app.services.rag_service import build_context_block, retrieve_relevant_chunks

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

RAG_SYSTEM_PROMPT = """
You are a thoughtful educational AI assistant.

Answer the user's question using the provided context.
Prefer the retrieved context over your general knowledge.

If the context is insufficient, say that the available source material does not fully answer the question.
Do not invent facts that are not supported by the context.

Write naturally and conversationally.
Do not use markdown section headings.
"""

RAG_SUGGESTIONS_PROMPT = """
You are a thoughtful educational AI assistant.

Use the provided context to answer the user's question.
Prefer the provided context over general knowledge.
If the context is insufficient, say so clearly and do not invent unsupported facts.

Return ONLY valid JSON with exactly these keys:
- answer
- suggested_questions

Rules:
- answer: 2 to 4 short paragraphs, clear, engaging, and natural
- do not use markdown headings
- suggested_questions: array of exactly 3 short follow-up questions
- do not include any text outside JSON
"""


def get_last_user_message(messages: list[ChatMessage]) -> str:
    for message in reversed(messages):
        if message.role == "user":
            return message.content

    raise ValueError("No user message found in conversation history")


def stream_answer_from_messages(messages: list[ChatMessage]) -> Generator[str, None, None]:
    user_query = get_last_user_message(messages)
    retrieved_chunks = retrieve_relevant_chunks(
        user_query, top_k=3, min_score=0.35)

    if not retrieved_chunks:
        fallback_text = (
            "I don’t have enough relevant source material in the current knowledge base "
            "to answer this confidently. Try asking something closer to the topics covered "
            "by the available documents."
        )
        yield fallback_text
        return

    context_block = build_context_block(retrieved_chunks)

    openai_input = [
        {
            "role": "user",
            "content": (
                f"Retrieved context:\n\n{context_block}\n\n"
                f"Conversation:\n\n"
            ),
        },
        *[
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ],
    ]

    try:
        stream = client.responses.create(
            model=MODEL,
            instructions=RAG_SYSTEM_PROMPT,
            input=openai_input,
            stream=True,
        )

        for event in stream:
            event_type = getattr(event, "type", None)

            if event_type == "response.output_text.delta":
                delta = getattr(event, "delta", "")
                if delta:
                    yield delta

            elif event_type == "error":
                raise RuntimeError("OpenAI stream emitted an error event")

    except Exception as e:
        print("STREAM SERVICE ERROR:", repr(e))
        raise


def explain_from_messages(messages: list[ChatMessage]) -> dict:
    user_query = get_last_user_message(messages)
    retrieved_chunks = retrieve_relevant_chunks(
        user_query, top_k=3, min_score=0.35)

    if not retrieved_chunks:
        return {
            "answer": (
                "I don’t have enough relevant source material in the current knowledge base "
                "to answer this confidently. Try asking something related to the documents "
                "that are currently available."
            ),
            "suggested_questions": [
                "How do black holes form?",
                "What is star dust?",
                "How is a supernova formed?",
            ],
            "sources": [],
        }

    context_block = build_context_block(retrieved_chunks)
    formatted_sources = []
    seen_sources = set()

    for chunk in retrieved_chunks:
        source_name = chunk["source"]

        if source_name in seen_sources:
            continue

        seen_sources.add(source_name)

    formatted_sources.append(
        {
            "source": source_name,
            "text": chunk["text"],
        }
    )

    openai_input = [
        {
            "role": "user",
            "content": (
                f"Retrieved context:\n\n{context_block}\n\n"
                f"Use this context to answer the conversation naturally."
            ),
        },
        *[
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ],
    ]

    response = client.responses.create(
        model=MODEL,
        instructions=RAG_SUGGESTIONS_PROMPT,
        input=openai_input,
        text={
            "format": {
                "type": "json_schema",
                "name": "chat_response",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "answer": {"type": "string"},
                        "suggested_questions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                            "maxItems": 3,
                        },
                    },
                    "required": ["answer", "suggested_questions"],
                },
                "strict": True,
            }
        },
    )

    raw_text = response.output_text
    if not raw_text:
        raise ValueError("Model returned empty output_text")

    parsed = json.loads(raw_text)

    return {
        "answer": parsed["answer"],
        "suggested_questions": parsed["suggested_questions"],
        "sources": formatted_sources,
    }
