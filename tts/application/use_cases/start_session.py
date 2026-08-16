from domain.entities.tts_session import TTSSession


class StartTTSSessionUseCase:
    def executer(self, session_id, voice: str) -> TTSSession:
        return TTSSession(session_id=session_id, voice=voice)