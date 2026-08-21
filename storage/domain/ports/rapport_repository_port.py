from abc import ABC, abstractmethod
from shared.domain.value_objects import SessionID


class RapportRepositoryPort(ABC):
    @abstractmethod
    async def sauvegarder_rapport(self, session_id: SessionID, rapport: dict) -> None:
        ...

    @abstractmethod
    async def recuperer_rapport(self, session_id: SessionID) -> dict | None:
        ...