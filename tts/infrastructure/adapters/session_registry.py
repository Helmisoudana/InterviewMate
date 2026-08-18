from typing import Optional
from shared.domain import SessionID
from tts.domain.entities.tts_session import TTSSession
from tts.domain.ports.tts_session_repository_port import TTSSessionRepositoryPort


class TTSSessionRegistry(TTSSessionRepositoryPort):
    def __init__(self) -> None:
        self._sessions: dict[str, TTSSession] = {}

    def save(self, session: TTSSession) -> None:
        self._sessions[session.session_id.value] = session

    def get(self, session_id: SessionID) -> Optional[TTSSession]:
        return self._sessions.get(session_id.value)

    def delete(self, session_id: SessionID) -> None:
        self._sessions.pop(session_id.value, None)