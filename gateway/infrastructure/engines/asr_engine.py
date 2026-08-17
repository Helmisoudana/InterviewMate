from typing import List, Protocol

from  domain.value_objects.session_id import SessionId
from  domain.value_objects.audio_chunk import AudioChunk
from  domain.value_objects.transcription_result import TranscriptionResult


class ASREngine(Protocol):

    async def demarrer_session(self, session_id: SessionId, language: str) -> None:
        ...

    async def traiter_chunk(self, session_id: SessionId, chunk: AudioChunk) -> List[TranscriptionResult]:
    
        ...

    async def finaliser(self, session_id: SessionId) -> TranscriptionResult:
    
        ...

    async def terminer_session(self, session_id: SessionId) -> None:
        
        ...