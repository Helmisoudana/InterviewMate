import os
from typing import AsyncGenerator
from openai import AsyncOpenAI

from agent.domain.ports.llm_port import LLMPort
from agent.domain.value_objects.message import Message


class GroqAdapter(LLMPort):
    """Adaptateur LLM pour l'API Groq (Couche Infrastructure)."""

    def __init__(
        self,
        model: str = "openai/gpt-oss-20b",  # <-- Remplacer par llama3-70b-8192 ou llama3-8b-8192
        api_key: str | None = None,
    ):
        self.model = model
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY non trouvée.")

        self._client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=key,
        )

    async def stream_completion(
        self, messages: list[Message]
    ) -> AsyncGenerator[str, None]:
        payload = [{"role": m.role, "content": m.content} for m in messages]

        stream = await self._client.chat.completions.create(
            model=self.model,
            messages=payload,
            stream=True,
            response_format={"type": "json_object"},
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content