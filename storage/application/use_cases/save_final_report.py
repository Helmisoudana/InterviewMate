from storage.domain.entities.rapport import RapportScorePersiste
from storage.domain.ports.storage_repository_port import StorageRepositoryPort


class SaveFinalReportUseCase:

    def __init__(self, repository: StorageRepositoryPort):
        self._repository = repository

    async def executer(self, rapport: RapportScorePersiste) -> RapportScorePersiste:
        return await self._repository.sauvegarder_rapport(rapport)
