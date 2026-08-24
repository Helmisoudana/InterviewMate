import logging
import time
import ollama
from agent.domain.ports.llm_port import LLMPort
from agent.domain.value_objects.message import Message

logger = logging.getLogger("latence")

NUM_PREDICT_DEFAUT = 1024
KEEP_ALIVE_DEFAUT = "30m"


class OllamaAdapter(LLMPort):
    def __init__(
        self,
        model: str = "llama3.1",
        num_predict: int = NUM_PREDICT_DEFAUT,
        keep_alive: str = KEEP_ALIVE_DEFAUT,
        temperature: float = 0.4,
    ):
        self.model = model
        self.num_predict = num_predict
        self.keep_alive = keep_alive
        self.temperature = temperature
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