from abc import ABC, abstractmethod
from shared.domain.value_objects import SessionID


class TranscriptRepositoryPort(ABC):
    @abstractmethod
    async def sauvegarder_transcript(self, session_id: SessionID, transcript: dict) -> None:
        ...

    @abstractmethod
    async def recuperer_historique(self, user_id: str) -> list[dict]:
        ...