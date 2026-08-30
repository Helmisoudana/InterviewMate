import logging
import os
import time

from dotenv import load_dotenv
import ollama
from agent.domain.ports.llm_port import LLMPort
from agent.domain.value_objects.message import Message

load_dotenv()

logger = logging.getLogger("latence")


class OllamaAdapter(LLMPort):
    def __init__(self):
        self.model = os.environ["MODEL"]
        self.num_predict = int(os.environ["NUM_PREDICT"])
        self.keep_alive = os.environ["KEEP_ALIVE"]
        self.temperature = float(os.environ["TEMPERATURE"])
        self._client = ollama.AsyncClient()

    async def stream_completion(self, messages: list[Message], response_schema: dict | None = None):
        payload = [{"role": m.role, "content": m.content} for m in messages]
        t0 = time.monotonic()
        nb_tokens = 0

        format_arg = response_schema if response_schema is not None else "json"
        try:
            async for chunk in await self._client.chat(
                model=self.model,
                messages=payload,
                stream=True,
                format=format_arg,
                keep_alive=self.keep_alive,
                options={
                    "num_predict": self.num_predict,
                    "temperature": self.temperature,
                },
            ):
                nb_tokens += 1
                yield chunk["message"]["content"]
        finally:
            duree = max(time.monotonic() - t0, 1e-6)
            logger.info(
                "[ollama] génération terminée : %d tokens en %.2fs (%.1f tok/s)",
                nb_tokens, duree, nb_tokens / duree,
            )