from storage.domain.ports.storage_repository_port import StorageRepositoryPort


class StartStorageSessionUseCase:

    def __init__(self, repository: StorageRepositoryPort) -> None:
        self._repository = repository

    async def executer(self, session_id: str) -> None:
        await self._repository.initialiser_entretien(session_id)