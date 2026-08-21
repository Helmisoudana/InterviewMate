from abc import ABC, abstractmethod
from storage.domain.entities.echange import EchangePersiste

class StorageRepositoryPort(ABC):

    @abstractmethod
    async def sauvegarder_dernier_echange(self, echange: EchangePersiste) -> EchangePersiste:
        """Persiste le dernier échange reçu et gère la session entretien dans PostgreSQL."""
        pass

    @abstractmethod
    async def mettre_a_jour_statut(self, session_id: str, statut: str) -> None:
        """Met à jour le statut de l'entretien (ex: 'TERMINE', 'INTERROMPU')."""
        pass