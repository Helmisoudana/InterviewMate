from shared.domain import SessionID
from gateway.domain.ports.session_client_port import SessionClientPort


class FakeSessionClient(SessionClientPort):
    def __init__(self, session_valide: bool = True) -> None:
        self.session_valide = session_valide
        self.coupures: list[str] = []
        self.reconnexions = 0

    async def valider_session(self, session_id: SessionID) -> bool:
        return self.session_valide

    async def notifier_coupure(self, session_id: SessionID, raison: str) -> None:
        self.coupures.append(raison)

    async def notifier_reconnexion(self, session_id: SessionID) -> None:
        self.reconnexions += 1