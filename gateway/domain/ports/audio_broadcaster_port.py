from typing import Protocol

from domain.value_objects.session_id import SessionId
from domain.value_objects.audio_chunk import AudioChunk


class AudioBroadcasterPort(Protocol):
    async def envoyer_audio_candidat(self, session_id: SessionId, chunk: AudioChunk) -> None: ...