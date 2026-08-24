from storage.domain.entities.echange import EchangePersiste
from storage.domain.ports.storage_repository_port import StorageRepositoryPort

class SaveLatestExchangeUseCase:

    def __init__(self, repository: StorageRepositoryPort):
        self._repository = repository

    async def sauvegarder(
        self, 
        session_id: str, 
        question_agent: str, 
        reponse_candidat: str, 
        qualite_percue: str | None = None
    ) -> EchangePersiste:
        echange = EchangePersiste(
            session_id=session_id,
            question_agent=question_agent,
            reponse_candidat=reponse_candidat,
            qualite_percue=qualite_percue
        )
        return await self._repository.sauvegarder_dernier_echange(echange)

    