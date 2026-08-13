from agent.domain.ports.llm_port import LLMPort, Message


class FakeLLMAdapter(LLMPort):
    async def stream_completion(self, messages: list[Message]):
        yield "Peux-tu m'expliquer la difference entre une liste et un tuple en Python ?"