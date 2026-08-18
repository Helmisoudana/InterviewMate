from session.domain.entities.interview_session import InterviewSession
from session.domain.value_objects.session_config import SessionConfig
from session.domain.ports.session_repository_port import SessionRepositoryPort
from shared.domain import SessionID


class CreateSessionUseCase:
    def __init__(self, store: SessionRepositoryPort) -> None:
        self._store = store

    def executer(self, session_id: SessionID, config: SessionConfig) -> None:
        session = InterviewSession(session_id=session_id, config=config)
        self._store.enregistrer(session)