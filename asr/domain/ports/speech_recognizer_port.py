from typing import Protocol
from shared.domain import SessionID, TranscriptionResult


class SpeechRecognizerPort(Protocol):
    async def transcrire_partiel(self, session_id: SessionID, audio_buffer: bytes, language: str) -> TranscriptionResult:
        ...

    async def transcrire_final(self, session_id: SessionID, audio_buffer: bytes, language: str) -> TranscriptionResult:
        ...