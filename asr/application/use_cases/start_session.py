from domain.entities.asr_session import ASRSession
from domain.value_objects.session_id import SessionId


class StartASRSessionUseCase:
    def executer(self, session_id: SessionId, language: str) -> ASRSession:
        return ASRSession(session_id=session_id, language=language)