from gateway.domain.ports.storage_client_port import StorageClientPort
from shared.domain import SessionID
from storage.application.use_cases.start_session import StartStorageSessionUseCase
from storage.application.use_cases.end_session import EndStorageSessionUseCase


class InProcessStorageClient(StorageClientPort):
    """Appel direct en process, meme pattern que InProcessASRClient/InProcessAgentClient/InProcessTTSClient."""

    def __init__(self, start_uc: StartStorageSessionUseCase, end_uc: EndStorageSessionUseCase) -> None:
        self._start_uc = start_uc
        self._end_uc = end_uc

    async def demarrer_session(self, session_id: SessionID) -> None:
        await self._start_uc.executer(str(session_id))

    async def terminer_session(self, session_id: SessionID) -> None:
        await self._end_uc.executer(str(session_id))