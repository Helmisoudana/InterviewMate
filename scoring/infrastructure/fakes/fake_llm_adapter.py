from scoring.domain.ports.llm_port import LLMPort
from shared.domain.value_objects import Message


class FakeLLMAdapter(LLMPort):
    async def stream_completion(self, messages: list[Message]):
        yield '{"competence": "rigueur_technique", "score": 0.7, "justification": "Evaluation fake pour test."}'