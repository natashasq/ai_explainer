import json
import os
from collections.abc import Generator

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.explain import ChatMessage

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

SYSTEM_PROMPT = """
You are a thoughtful educational AI assistant.

Your job is to answer the user's question in a natural, conversational, smooth way.
Do not sound robotic, overly formal, or like a textbook.
The answer should feel like a smart human explaining something clearly.

Answer in plain text.
Do not use markdown.
Do not use section headings.
Write 2 to 4 short paragraphs.
Use an analogy only if it helps naturally.
"""

SUGGESTIONS_PROMPT = """
You are a thoughtful educational AI assistant.

Return ONLY valid JSON with exactly these keys:
- answer
- suggested_questions

Rules:
- answer: 2 to 4 short paragraphs, clear, engaging, and natural
- use smooth transitions
- include an analogy only if it helps naturally
- do not split the answer into labeled sections
- avoid markdown
- suggested_questions: array of exactly 3 short follow-up questions
- do not include any text outside JSON
"""


def stream_answer_from_messages(messages: list[ChatMessage]) -> Generator[str, None, None]:
    openai_input = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]

    stream = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
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
            error_message = getattr(event, "message", "Streaming error")
            raise RuntimeError(error_message)


def explain_from_messages(messages: list[ChatMessage]) -> dict:
    openai_input = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]

    response = client.responses.create(
        model=MODEL,
        instructions=SUGGESTIONS_PROMPT,
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
    }
