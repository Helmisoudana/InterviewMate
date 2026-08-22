from typing import Protocol
from shared.domain import SessionID


class StorageClientPort(Protocol):

    async def demarrer_session(self, session_id: SessionID , poste:str , language : str , difficulte : str , duree : str) -> None: ...
    async def terminer_session(self, session_id: SessionID) -> None: ...