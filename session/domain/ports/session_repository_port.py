from typing import Protocol, Optional, List, Tuple
from shared.domain import SessionID
from session.domain.entities.interview_session import InterviewSession

class SessionRepositoryPort(Protocol):
    def enregistrer(self, session: InterviewSession) -> None:
        ...

    def obtenir(self, session_id: SessionID) -> Optional[InterviewSession]:
        ...

    def retirer(self, session_id: SessionID) -> None:
        ...

    def tout_lister(self) -> List[Tuple[str, InterviewSession]]:
        ...
