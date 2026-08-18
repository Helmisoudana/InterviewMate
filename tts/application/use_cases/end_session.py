from shared.domain import SessionID
from tts.domain.ports.tts_session_repository_port import TTSSessionRepositoryPort


class EndTTSSessionUseCase:
    def __init__(self, session_repo: TTSSessionRepositoryPort) -> None:
        self._session_repo = session_repo

    def executer(self, session_id: SessionID) -> None:
        self._session_repo.delete(session_id)