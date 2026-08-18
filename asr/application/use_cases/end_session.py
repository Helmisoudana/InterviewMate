from shared.domain import SessionID
from asr.domain.ports.asr_session_repository_port import ASRSessionRepositoryPort


class EndASRSessionUseCase:
    def __init__(self, session_repo: ASRSessionRepositoryPort) -> None:
        self._session_repo = session_repo

    def executer(self, session_id: SessionID) -> None:
        self._session_repo.delete(session_id)