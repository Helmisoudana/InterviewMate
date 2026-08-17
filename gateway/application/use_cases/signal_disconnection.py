from domain.entities.entities import GatewaySession
from domain.ports.session_client_port import SessionClientPort


class SignalDisconnectionUseCase:
    def __init__(self, session_client: SessionClientPort) -> None:
        self._session_client = session_client

    async def executer(self, session: GatewaySession, raison: str) -> None:
        session.signaler_coupure()
        await self._session_client.notifier_coupure(session.session_id, raison)