from abc import ABC, abstractmethod
from scoring.domain.entities.rapport_final import RapportFinal


class StorageClientPort(ABC):
    @abstractmethod
    async def sauvegarder_rapport(self, rapport: RapportFinal) -> None:
        ...