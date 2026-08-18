from typing import Protocol, Optional
from shared.domain import SessionID
from asr.domain.entities.asr_session import ASRSession

class ASRSessionRepositoryPort(Protocol):
    def save(self, session: ASRSession) -> None:
        ...

    def get(self, session_id: SessionID) -> Optional[ASRSession]:
        ...

    def delete(self, session_id: SessionID) -> None:
        ...
