from shared.domain.value_objects import SessionID, AudioChunk, TranscriptionResult
from asr.domain.ports.asr_session_repository_port import ASRSessionRepositoryPort 
from asr.domain.ports.speech_recognizer_port import SpeechRecognizerPort


class ProcessAudioChunkUseCase:
    def __init__(
        self,
        recognizer: SpeechRecognizerPort,
        session_repo: ASRSessionRepositoryPort,
        intervalle_chunks: int = 5,
    ) -> None:
    
        self._recognizer = recognizer
        self._session_repo = session_repo
        self._intervalle_chunks = max(1, intervalle_chunks)

    async def executer(self, session_id: SessionID, chunk: AudioChunk) -> TranscriptionResult:
        session = self._session_repo.get(session_id)
        if session is None:
            raise ValueError(f"Session ASR inconnue : {session_id.value}")

        session.ajouter_chunk(chunk)
        self._session_repo.save(session)
        if session.nombre_chunks_recus % self._intervalle_chunks != 0:
            return TranscriptionResult(session_id=session_id, is_final=False, text="", confidence=0.0)

        return await self._recognizer.transcrire_partiel(
            session_id=session_id,
            audio_buffer=session.obtenir_buffer(),
            language=session.language,
        )