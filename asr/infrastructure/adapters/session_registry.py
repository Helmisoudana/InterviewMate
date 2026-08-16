
from asr.domain.entities.asr_session import ASRSession
from asr.domain.value_objects.session_id import SessionId


class ASRSessionRegistry:
    def __init__(self) -> None:
        self._sessions: dict[str, ASRSession] = {}

    def enregistrer(self, session: ASRSession) -> None:
        self._sessions[session.session_id.value] = session

    def obtenir(self, session_id: SessionId) -> ASRSession | None:
        return self._sessions.get(session_id.value)

    def retirer(self, session_id: SessionId) -> None:
        self._sessions.pop(session_id.value, None)