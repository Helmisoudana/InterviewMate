from domain.value_objects.session_id import SessionId


class FakeSessionClient:
    def __init__(self, session_valide: bool = True) -> None:
        self.session_valide = session_valide
        self.coupures: list[str] = []
        self.reconnexions = 0

    async def valider_session(self, session_id: SessionId) -> bool:
        return self.session_valide

    async def notifier_coupure(self, session_id: SessionId, raison: str) -> None:
        self.coupures.append(raison)

    async def notifier_reconnexion(self, session_id: SessionId) -> None:
        self.reconnexions += 1