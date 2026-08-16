from  domain.entities.asr_session import ASRSession
from  domain.value_objects.transcription_result import TranscriptionResult
from  domain.ports.speech_recognizer_port import SpeechRecognizerPort


class FinalizeTurnUseCase:
    def __init__(self, recognizer: SpeechRecognizerPort) -> None:
        self._recognizer = recognizer

    async def executer(self, session: ASRSession) -> TranscriptionResult:
        resultat = await self._recognizer.transcrire_final(
            audio_buffer=session.obtenir_buffer(),
            language=session.language,
        )
        session.reinitialiser_buffer()
        return resultat