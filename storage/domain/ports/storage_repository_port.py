from abc import ABC, abstractmethod
from typing import List
from storage.domain.entities.echange import EchangePersiste
from storage.domain.entities.rapport import RapportScorePersiste

class StorageRepositoryPort(ABC):

    @abstractmethod
    async def sauvegarder_dernier_echange(self, echange: EchangePersiste) -> EchangePersiste:
        """Persiste le dernier échange reçu et gère la session entretien dans PostgreSQL."""
        pass

    @abstractmethod
    async def mettre_a_jour_statut(self, session_id: str, statut: str) -> None:
        """Met à jour le statut de l'entretien (ex: 'TERMINE', 'INTERROMPU')."""
        pass

    @abstractmethod
    async def recuperer_echanges_par_session(self, session_id: str) -> List[EchangePersiste]:
        """Récupère tous les échanges d'un entretien, ordonnés, pour le module scoring."""
        pass

    @abstractmethod
    async def sauvegarder_rapport(self, rapport: RapportScorePersiste) -> RapportScorePersiste:
        """Persiste le rapport final de scoring pour un entretien."""
        pass