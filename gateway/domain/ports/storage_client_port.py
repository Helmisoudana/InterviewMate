from typing import Protocol
from shared.domain import SessionID


class StorageClientPort(Protocol):

    async def demarrer_session(self, session_id: SessionID) -> None: ...
    async def terminer_session(self, session_id: SessionID) -> None: ...