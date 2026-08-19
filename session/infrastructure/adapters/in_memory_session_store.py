from typing import Optional, List, Tuple
from session.domain.entities.interview_session import InterviewSession
from shared.domain import SessionID
from session.domain.ports.session_repository_port import SessionRepositoryPort


class InMemorySessionStore(SessionRepositoryPort):
    """Dict en mémoire : accès O(1), pas de latence réseau."""

    def __init__(self) -> None:
        self._sessions: dict[str, InterviewSession] = {}

    def enregistrer(self, session: InterviewSession) -> None:
        self._sessions[session.session_id.value] = session

    def obtenir(self, session_id: SessionID) -> Optional[InterviewSession]:
        return self._sessions.get(session_id.value)

    def retirer(self, session_id: SessionID) -> None:
        self._sessions.pop(session_id.value, None)

    def tout_lister(self) -> List[Tuple[str, InterviewSession]]:
        return list(self._sessions.items())