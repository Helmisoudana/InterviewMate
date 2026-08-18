from abc import ABC, abstractmethod
from typing import AsyncIterator
from agent.domain.value_objects.message import Message


class LLMPort(ABC):
    @abstractmethod
    async def stream_completion(self, messages: list[Message]) -> AsyncIterator[str]:
        ...