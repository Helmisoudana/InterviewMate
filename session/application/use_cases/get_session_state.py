from domain.entities.interview_session import InterviewSession
from domain.value_objects.session_id import SessionId
from domain.exceptions.exceptions import SessionInconnueError


class GetSessionStateUseCase:
    def __init__(self, store) -> None:
        self._store = store

    def executer(self, session_id: SessionId) -> InterviewSession:
        session = self._store.obtenir(session_id)
        if session is None:
            raise SessionInconnueError(f"Session {session_id.value} inconnue")
        return session