from  domain.entities.asr_session import ASRSession
from  domain.value_objects.audio_chunk import AudioChunk
from  domain.value_objects.transcription_result import TranscriptionResult
from  domain.ports.speech_recognizer_port import SpeechRecognizerPort


class ProcessAudioChunkUseCase:
    def __init__(self, recognizer: SpeechRecognizerPort) -> None:
        self._recognizer = recognizer

    async def executer(self, session: ASRSession, chunk: AudioChunk) -> TranscriptionResult:
        session.ajouter_chunk(chunk)
        return await self._recognizer.transcrire_partiel(
            audio_buffer=session.obtenir_buffer(),
            language=session.language,
        )