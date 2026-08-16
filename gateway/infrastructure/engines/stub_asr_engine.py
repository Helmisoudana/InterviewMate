import asyncio
from typing import List

from  domain.value_objects.session_id import SessionId
from  domain.value_objects.audio_chunk import AudioChunk
from  domain.value_objects.transcription_result import TranscriptionResult


class StubASREngine:
    """Moteur factice : renvoie un texte fixe, juste pour tester le câblage."""

    async def demarrer_session(self, session_id: SessionId, language: str) -> None:
        pass

    async def traiter_chunk(self, session_id: SessionId, chunk: AudioChunk) -> List[TranscriptionResult]:
        await asyncio.sleep(0)  # simule un traitement async
        return [TranscriptionResult(type="partial", text="je pense que", confidence=0.6)]

    async def finaliser(self, session_id: SessionId) -> TranscriptionResult:
        return TranscriptionResult(type="final", text="je pense que le pattern singleton est utile", confidence=0.92)

    async def terminer_session(self, session_id: SessionId) -> None:
        pass