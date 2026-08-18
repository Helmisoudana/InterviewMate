from typing import AsyncIterator
from shared.domain import SessionID, AudioChunk
from gateway.domain.ports.tts_client_port import TTSClientPort


class FakeTTSClient(TTSClientPort):
    def __init__(self) -> None:
        self.textes_demandes: list[str] = []

    async def demarrer_session(self, session_id: SessionID, voice: str) -> None:
        pass

    async def terminer_session(self, session_id: SessionID) -> None:
        pass

    async def synthetiser_stream(self, session_id: SessionID, texte: str) -> AsyncIterator[AudioChunk]:
        self.textes_demandes.append(texte)
        yield AudioChunk(session_id=session_id, data=b"\x00" * 320, is_final=True)