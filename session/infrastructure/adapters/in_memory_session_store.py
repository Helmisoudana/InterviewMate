from domain.entities.interview_session import InterviewSession
from domain.value_objects.session_id import SessionId


class InMemorySessionStore:
    """Dict en mémoire : accès O(1), pas de latence réseau."""

    def __init__(self) -> None:
        self._sessions: dict[str, InterviewSession] = {}

    def enregistrer(self, session: InterviewSession) -> None:
        self._sessions[session.session_id.value] = session

    def obtenir(self, session_id: SessionId) -> InterviewSession | None:
        return self._sessions.get(session_id.value)

    def retirer(self, session_id: SessionId) -> None:
        self._sessions.pop(session_id.value, None)

    def tout_lister(self):
        return list(self._sessions.items())