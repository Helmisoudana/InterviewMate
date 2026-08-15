from agent.domain.ports.llm_port import LLMPort, Message


class FakeLLMAdapter(LLMPort):
    def __init__(self):
        self._questions = [
            "Peux-tu m'expliquer la difference entre une liste et un tuple en Python ?",
            "Comment gererais-tu une exception dans une API REST ?",
            "Parle-moi d'une fois ou tu as du resoudre un bug difficile.",
        ]
        self._index = 0

    async def stream_completion(self, messages: list[Message]):
        question = self._questions[self._index % len(self._questions)]
        self._index += 1
        yield question