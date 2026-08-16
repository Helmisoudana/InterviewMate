from typing import AsyncIterator

from domain.value_objects.session_id import SessionId


class InProcessTTSClient:
    def __init__(self, engine) -> None:
        self._engine = engine

    async def demarrer_session(self, session_id: SessionId, voice: str) -> None:
        await self._engine.demarrer_session(session_id, voice)

    def synthetiser_stream(self, session_id: SessionId, texte: str) -> AsyncIterator[bytes]:
        return self._engine.synthetiser(session_id, texte)

    async def terminer_session(self, session_id: SessionId) -> None:
        await self._engine.terminer_session(session_id)