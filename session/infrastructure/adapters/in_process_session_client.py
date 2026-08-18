
from gateway.domain.value_objects.session_id import SessionId as GatewaySessionId
from session.domain.value_objects.session_id import SessionId as SessionModuleId
from session.domain.ports.session_service_port import SessionServicePort
from session.domain.exceptions.exceptions import SessionInconnueError


class InProcessSessionClient:
    def __init__(self, session_service: SessionServicePort) -> None:
        self._session_service = session_service

    async def valider_session(self, session_id: GatewaySessionId) -> bool:
        return self._session_service.session_existe(SessionModuleId(session_id.value))

    async def notifier_coupure(self, session_id: GatewaySessionId, raison: str) -> None:
        try:
            self._session_service.noter_activite(SessionModuleId(session_id.value))
        except SessionInconnueError:
            pass

    async def notifier_reconnexion(self, session_id: GatewaySessionId) -> None:
        try:
            self._session_service.noter_activite(SessionModuleId(session_id.value))
        except SessionInconnueError:
            pass