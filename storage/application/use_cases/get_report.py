from typing import Optional
from storage.domain.entities.rapport import RapportScorePersiste
from storage.domain.ports.storage_repository_port import StorageRepositoryPort
class GetReportUseCase:
    """Expose la lecture d'un rapport existant. Utilise par scoring pour le pattern get-or-generate."""

    def __init__(self, repository: StorageRepositoryPort):
        self._repository = repository

    async def executer(self, session_id: str) -> Optional[RapportScorePersiste]:
        return await self._repository.recuperer_rapport(session_id)