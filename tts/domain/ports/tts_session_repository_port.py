from typing import Protocol, Optional
from shared.domain import SessionID
from tts.domain.entities.tts_session import TTSSession

class TTSSessionRepositoryPort(Protocol):
    def save(self, session: TTSSession) -> None:
        ...

    def get(self, session_id: SessionID) -> Optional[TTSSession]:
        ...

    def delete(self, session_id: SessionID) -> None:
        ...
