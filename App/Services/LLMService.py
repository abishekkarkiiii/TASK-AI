import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY is not configured"
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)


def generate_answer(
    context: str,
    question: str,
    history: list[dict[str, str]]
) -> str:

    messages = [
        {
            "role": "system",
            "content": """
You are a helpful assistant.

Answer the user's question using the provided context
and conversation history.

Rules:
- Use the provided context as the primary source.
- Use conversation history to understand references
  such as "it", "that", "those", or "the previous one".
- Do not invent information.
- If the answer is not available, say you don't know.
"""
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": f"""
Context:

{context}

Current question:

{question}
"""
        }
    )

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages
    )

    return response.choices[0].message.content