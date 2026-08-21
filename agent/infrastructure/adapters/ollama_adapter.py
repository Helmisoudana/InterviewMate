import asyncio
import logging
import queue
import time
import ollama
from agent.domain.ports.llm_port import LLMPort
from agent.domain.value_objects.message import Message

_SENTINEL = object()
logger = logging.getLogger("latence")

NUM_PREDICT_DEFAUT = 220

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

    async def stream_completion(self, messages: list[Message]):
        payload = [{"role": m.role, "content": m.content} for m in messages]
        file_tokens: queue.Queue = queue.Queue()
        loop = asyncio.get_event_loop()

        def produire() -> None:
            t0 = time.monotonic()
            nb_tokens = 0
            try:
                for chunk in ollama.chat(
                    model=self.model,
                    messages=payload,
                    stream=True,
                    format="json",
                    keep_alive=self.keep_alive,
                    options={
                        "num_predict": self.num_predict,
                        "temperature": self.temperature,
                    },
                ):
                    nb_tokens += 1
                    file_tokens.put(chunk["message"]["content"])
            except Exception as e:
                file_tokens.put(e)
            finally:
                logger.info(
                    "[ollama] génération terminée : %d tokens en %.2fs (%.1f tok/s)",
                    nb_tokens, time.monotonic() - t0,
                    nb_tokens / max(time.monotonic() - t0, 1e-6),
                )
                file_tokens.put(_SENTINEL)

        loop.run_in_executor(None, produire)

        while True:
            item = await asyncio.to_thread(file_tokens.get)
            if item is _SENTINEL:
                break
            if isinstance(item, Exception):
                raise item
            yield item