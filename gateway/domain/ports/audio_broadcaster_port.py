from typing import Protocol
from shared.domain import SessionID, AudioChunk


class AudioBroadcasterPort(Protocol):
    async def envoyer_audio_candidat(self, session_id: SessionID, chunk: AudioChunk) -> None: ...

    async def envoyer_texte(self, session_id: SessionID, type_message: str, texte: str) -> None:
        ...