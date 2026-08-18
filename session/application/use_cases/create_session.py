from domain.entities.interview_session import InterviewSession
from domain.value_objects.session_id import SessionId
from domain.value_objects.session_config import SessionConfig


class CreateSessionUseCase:
    def executer(self, session_id: SessionId, config: SessionConfig) -> InterviewSession:
        return InterviewSession(session_id=session_id, config=config)