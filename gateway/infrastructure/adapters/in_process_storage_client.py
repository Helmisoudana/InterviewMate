from gateway.domain.ports.storage_client_port import StorageClientPort
from shared.domain import SessionID
from storage.application.use_cases.start_session import StartStorageSessionUseCase
from storage.application.use_cases.end_session import EndStorageSessionUseCase
from agent.domain.entities.interview import Interview
from datetime import datetime , timezone



class InProcessStorageClient(StorageClientPort):

    def __init__(self, start_uc: StartStorageSessionUseCase, end_uc: EndStorageSessionUseCase) -> None:
        self._start_uc = start_uc
        self._end_uc = end_uc

    async def demarrer_session(self, session_id: SessionID , poste: str ,langue : str , difficulte :str , timestamp:str ) -> None:
        timestamp_actuel = datetime.now(timezone.utc)
        await self._start_uc.executer(str(session_id) , str(poste) , str(langue) , str(difficulte) , timestamp_actuel)

    async def terminer_session(self, session_id: SessionID) -> None:
        await self._end_uc.executer(str(session_id))