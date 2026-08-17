import asyncio
import ollama
from agent.domain.ports.llm_port import LLMPort, Message


class OllamaAdapter(LLMPort):
    def __init__(self, model: str = "llama3"):
        self.model = model

    async def stream_completion(self, messages: list[Message]):
        payload = [{"role": m.role, "content": m.content} for m in messages]

        def appel_bloquant():
            return list(ollama.chat(model=self.model, messages=payload, stream=True))

        chunks = await asyncio.to_thread(appel_bloquant)

        for chunk in chunks:
            yield chunk["message"]["content"]