from typing import List
from storage.domain.entities.echange import EchangePersiste
from storage.domain.ports.storage_repository_port import StorageRepositoryPort


class GetSessionTranscriptUseCase:

    def __init__(self, repository: StorageRepositoryPort):
        self._repository = repository

    async def executer(self, session_id: str) -> List[EchangePersiste]:
        return await self._repository.recuperer_echanges_par_session(session_id)
