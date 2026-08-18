from domain.value_objects.session_id import SessionId


class InProcessAgentClient:
    def __init__(self, engine) -> None:
        self._engine = engine

    async def demarrer_session(self, session_id: SessionId) -> None:
        await self._engine.demarrer_session(session_id.value)

    async def traiter_reponse(self, session_id: SessionId, texte_reponse: str) -> tuple[str, bool]:
        return await self._engine.traiter_reponse(session_id.value, texte_reponse)

    async def terminer_session(self, session_id: SessionId) -> None:
        await self._engine.terminer_session(session_id.value)