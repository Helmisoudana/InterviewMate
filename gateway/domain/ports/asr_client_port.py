from typing import Protocol

from gateway.domain.value_objects.session_id import SessionId
from gateway.domain.value_objects.audio_chunk import AudioChunk


class ASRClientPort(Protocol):
    async def envoyer_chunk(self, session_id: SessionId, chunk: AudioChunk) -> None: ...
    async def signaler_fin_de_tour(self, session_id: SessionId) -> None: ...