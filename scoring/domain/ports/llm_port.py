from abc import ABC, abstractmethod
from typing import AsyncIterator
from shared.domain.value_objects import Message


class LLMPort(ABC):
    @abstractmethod
    async def stream_completion(self, messages: list[Message]) -> AsyncIterator[str]:
        ...