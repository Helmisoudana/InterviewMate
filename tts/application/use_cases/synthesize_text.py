from typing import AsyncIterator
from shared.domain import SessionID, AudioChunk
from tts.domain.ports.speech_synthesizer_port import SpeechSynthesizerPort
from tts.domain.ports.tts_session_repository_port import TTSSessionRepositoryPort


class SynthesizeTextUseCase:
    def __init__(self, synthesizer: SpeechSynthesizerPort, session_repo: TTSSessionRepositoryPort) -> None:
        self._synthesizer = synthesizer
        self._session_repo = session_repo

    async def executer(self, session_id: SessionID, texte: str) -> AsyncIterator[AudioChunk]:
        session = self._session_repo.get(session_id)
        if session is None:
            raise ValueError(f"Session TTS inconnue : {session_id.value}")

        sequence = 0
        async for chunk_bytes in self._synthesizer.synthetiser(texte, session.voice):
            sequence += 1
            yield AudioChunk(session_id=session_id, data=chunk_bytes, is_final=False)