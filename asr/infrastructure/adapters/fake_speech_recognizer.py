import asyncio
from shared.domain import SessionID, TranscriptionResult


class FakeSpeechRecognizer:
    async def transcrire_partiel(self, session_id: SessionID, audio_buffer: bytes, language: str) -> TranscriptionResult:
        await asyncio.sleep(0)
        return TranscriptionResult(
            session_id=session_id,
            text="je pense que",
            is_final=False,
            confidence=0.6
        )

    async def transcrire_final(self, session_id: SessionID, audio_buffer: bytes, language: str) -> TranscriptionResult:
        await asyncio.sleep(0)
        return TranscriptionResult(
            session_id=session_id,
            text="je pense que le pattern singleton est utile ici",
            is_final=True,
            confidence=0.91,
        )