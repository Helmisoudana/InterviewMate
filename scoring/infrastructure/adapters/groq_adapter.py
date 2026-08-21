import os
from openai import AsyncOpenAI
from scoring.domain.ports.llm_port import LLMPort
from shared.domain.value_objects import Message


class GroqAdapter(LLMPort):
    def __init__(self, model: str = "llama-3.3-70b-versatile", api_key: str | None = None):
        self.model = model
        self._client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key or os.environ["GROQ_API_KEY"],
        )

    async def stream_completion(self, messages: list[Message]):
        payload = [{"role": m.role, "content": m.content} for m in messages]

        stream = await self._client.chat.completions.create(
            model=self.model,
            messages=payload,
            stream=True,
            response_format={"type": "json_object"},
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta