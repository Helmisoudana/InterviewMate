import time
import asyncio
import logging
import ollama
from agent.domain.ports.llm_port import LLMPort
from agent.domain.value_objects.message import Message

logger = logging.getLogger("agent.ollama")


class OllamaAdapter(LLMPort):
    def __init__(self, model: str = "llama3", keep_alive: str = "30m", num_predict: int = 200):
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

        debut = time.perf_counter()
        chunks = await asyncio.to_thread(appel_bloquant)
        duree = time.perf_counter() - debut
        logger.info("[TIMING] Agent (Ollama, generation question) : %.2fs", duree)

        for chunk in chunks:
            yield chunk["message"]["content"]