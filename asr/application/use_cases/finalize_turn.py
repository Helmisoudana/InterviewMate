from shared.domain import SessionID, TranscriptionResult
from asr.domain.ports.speech_recognizer_port import SpeechRecognizerPort
from asr.domain.ports.asr_session_repository_port import ASRSessionRepositoryPort


class FinalizeTurnUseCase:
    def __init__(self, recognizer: SpeechRecognizerPort, session_repo: ASRSessionRepositoryPort) -> None:
        self._recognizer = recognizer
        self._session_repo = session_repo

    async def executer(self, session_id: SessionID) -> TranscriptionResult:
        session = self._session_repo.get(session_id)
        if session is None:
            raise ValueError(f"Session ASR inconnue : {session_id.value}")

        resultat = await self._recognizer.transcrire_final(
            session_id=session_id,
            audio_buffer=session.obtenir_buffer(),
            language=session.language,
        )
        session.reinitialiser_buffer()
        self._session_repo.save(session)
        return resultat