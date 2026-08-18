from typing import Protocol
from shared.domain import SessionID, AudioChunk


class AudioBroadcasterPort(Protocol):
    async def envoyer_audio_candidat(self, session_id: SessionID, chunk: AudioChunk) -> None: ...