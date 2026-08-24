from storage.domain.ports.storage_repository_port import StorageRepositoryPort

class UpdateStatusUseCase:
    def __init__(self , repository : StorageRepositoryPort):
        self.repository= repository
    async def executer(self, session_id: str, statut: str) -> None:
            await self.repository.mettre_a_jour_statut(session_id, statut)