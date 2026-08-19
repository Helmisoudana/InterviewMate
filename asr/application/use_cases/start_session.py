from asr.domain.entities.asr_session import ASRSession
from shared.domain import SessionID
from asr.domain.ports.asr_session_repository_port import ASRSessionRepositoryPort


class StartASRSessionUseCase:
    def __init__(self, session_repo: ASRSessionRepositoryPort) -> None:
        self._session_repo = session_repo

    def executer(self, session_id: SessionID, language: str) -> None:
        session = ASRSession(session_id=session_id, language=language)
        self._session_repo.save(session)