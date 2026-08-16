from domain.entities.entities import GatewaySession
from domain.ports.session_client_port import SessionClientPort
from domain.exceptions.exceptions import SessionInvalideError


class StartSessionUseCase:
    def __init__(self, session_client: SessionClientPort) -> None:
        self._session_client = session_client

    async def executer(self, session: GatewaySession) -> None:
        valide = await self._session_client.valider_session(session.session_id)
        if not valide:
            session.invalider()
            raise SessionInvalideError(f"Session {session.session_id.value} invalide ou expirée")
        session.activer()