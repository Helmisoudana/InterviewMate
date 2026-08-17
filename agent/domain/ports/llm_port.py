# agent/domain/ports/llm_port.py
from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass


@dataclass
class Message:
    role: str       
    content: str


class LLMPort(ABC):
    @abstractmethod
    async def stream_completion(self, messages: list[Message]) -> AsyncIterator[str]:
        ...