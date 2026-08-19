from shared.domain.value_objects import SessionID, AudioChunk, TranscriptionResult
from asr.domain.ports.asr_session_repository_port import ASRSessionRepositoryPort 
from asr.domain.ports.speech_recognizer_port import SpeechRecognizerPort


class ProcessAudioChunkUseCase:
    def __init__(self, recognizer: SpeechRecognizerPort, session_repo: ASRSessionRepositoryPort) -> None:
        self._recognizer = recognizer
        self._session_repo = session_repo

    async def executer(self, session_id: SessionID, chunk: AudioChunk) -> TranscriptionResult:
        session = self._session_repo.get(session_id) 
        if session is None:
            raise ValueError(f"Session ASR inconnue : {session_id.value}")
        
        session.ajouter_chunk(chunk)
        self._session_repo.save(session)
        
        return await self._recognizer.transcrire_partiel(
            session_id=session_id,
            audio_buffer=session.obtenir_buffer(),
            language=session.language,
        )