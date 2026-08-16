from typing import AsyncIterator, Protocol

from domain.value_objects.session_id import SessionId


class TTSClientPort(Protocol):

    def synthetiser_stream(self, session_id: SessionId, texte: str) -> AsyncIterator[bytes]:
        ...