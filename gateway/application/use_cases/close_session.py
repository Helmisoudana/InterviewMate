from domain.entities.entities import GatewaySession


class CloseSessionUseCase:
    async def executer(self, session: GatewaySession, raison: str = "fin normale") -> None:
        session.fermer()