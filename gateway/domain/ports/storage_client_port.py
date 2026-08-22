from typing import Protocol
from shared.domain import SessionID


class StorageClientPort(Protocol):
    """Meme forme que ASRClientPort/AgentClientPort/TTSClientPort."""

    async def demarrer_session(self, session_id: SessionID) -> None: ...
    async def terminer_session(self, session_id: SessionID) -> None: ...