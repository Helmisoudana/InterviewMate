from abc import ABC, abstractmethod
from agent.domain.entities.interview import Interview


class SessionRepositoryPort(ABC):
    @abstractmethod
    async def get(self, session_id: str) -> Interview:
        ...

    @abstractmethod
    async def save(self, session_id: str, interview: Interview) -> None:
        ...