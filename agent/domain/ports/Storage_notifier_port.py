from abc import ABC, abstractmethod
from agent.domain.entities.echange import Echange


class StorageNotifierPort(ABC):
    @abstractmethod
    async def notifier_echange_termine(self, session_id: str, echange: Echange) -> None:
        ...

