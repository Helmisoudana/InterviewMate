from shared.domain import SessionID
from tts.domain.entities.tts_session import TTSSession
from tts.domain.ports.tts_session_repository_port import TTSSessionRepositoryPort


class StartTTSSessionUseCase:
    def __init__(self, session_repo: TTSSessionRepositoryPort) -> None:
        self._session_repo = session_repo

    def executer(self, session_id: SessionID, voice: str) -> None:
        session = TTSSession(session_id=session_id, voice=voice)
        self._session_repo.save(session)