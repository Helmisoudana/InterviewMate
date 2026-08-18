from typing import Optional
from asr.domain.entities.asr_session import ASRSession
from shared.domain import SessionID
from asr.domain.ports.asr_session_repository_port import ASRSessionRepositoryPort


class ASRSessionRegistry(ASRSessionRepositoryPort):
    def __init__(self) -> None:
        self._sessions: dict[str, ASRSession] = {}

    def save(self, session: ASRSession) -> None:
        self._sessions[session.session_id.value] = session

    def get(self, session_id: SessionID) -> Optional[ASRSession]:
        return self._sessions.get(session_id.value)

    def delete(self, session_id: SessionID) -> None:
        self._sessions.pop(session_id.value, None)