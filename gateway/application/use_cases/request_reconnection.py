from domain.entities.entities import GatewaySession
from domain.ports.session_client_port import SessionClientPort
from domain.exceptions.exceptions import SessionInvalideError


class RequestReconnectionUseCase:
    def __init__(self, session_client: SessionClientPort) -> None:
        self._session_client = session_client

    async def executer(self, session: GatewaySession) -> None:
        session.entrer_en_reconnexion()  # lève SessionFermeeError si déjà fermée
        valide = await self._session_client.valider_session(session.session_id)
        if not valide:
            session.invalider()
            raise SessionInvalideError(f"Session {session.session_id.value} n'est plus valide")
        session.activer()
        await self._session_client.notifier_reconnexion(session.session_id)