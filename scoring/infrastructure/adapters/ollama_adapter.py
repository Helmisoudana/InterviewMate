import asyncio
import ollama
from scoring.domain.ports.llm_port import LLMPort
from shared.domain.value_objects import Message


class OllamaAdapter(LLMPort):
    def __init__(self, model: str = "llama3:latest", keep_alive: str = "30m", num_predict: int = 150):
        self.model = model
        self.keep_alive = keep_alive
        self.num_predict = num_predict

    async def stream_completion(self, messages: list[Message]):
        payload = [{"role": m.role, "content": m.content} for m in messages]

        def appel_bloquant():
            return list(ollama.chat(
                model=self.model,
                messages=payload,
                stream=True,
                format="json",
                keep_alive=self.keep_alive,
                options={"num_predict": self.num_predict},
            ))

        chunks = await asyncio.to_thread(appel_bloquant)
        for chunk in chunks:
            yield chunk["message"]["content"]