from abc import ABC, abstractmethod
from typing import List, Optional
from storage.domain.entities.echange import EchangePersiste
from storage.domain.entities.rapport import RapportScorePersiste

class StorageRepositoryPort(ABC):

    @abstractmethod
    async def initialiser_entretien(self, session_id: str , poste : str , langue : str , difficulte : str , timestamp : str) -> None:
        pass

    @abstractmethod
    async def sauvegarder_dernier_echange(self, echange: EchangePersiste) -> EchangePersiste:
        pass

    @abstractmethod
    async def mettre_a_jour_statut(self, session_id: str, statut: str) -> None:
        pass

    @abstractmethod
    async def recuperer_echanges_par_session(self, session_id: str) -> List[EchangePersiste]:
        pass

    @abstractmethod
    async def sauvegarder_rapport(self, rapport: RapportScorePersiste) -> RapportScorePersiste:
        pass
    @abstractmethod
    async def recuperer_rapport(self, session_id: str) -> Optional[RapportScorePersiste]:
        pass