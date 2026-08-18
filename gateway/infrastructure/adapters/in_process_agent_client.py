from shared.domain import SessionID
from gateway.domain.ports.agent_client_port import AgentClientPort
from agent.application.use_cases.start_session import StartAgentSessionUseCase
from agent.application.use_cases.conduire_entretien import ConduireEntretienUseCase
from agent.application.use_cases.end_session import EndAgentSessionUseCase


class InProcessAgentClient(AgentClientPort):
    def __init__(
        self,
        start_uc: StartAgentSessionUseCase,
        conduire_uc: ConduireEntretienUseCase,
        end_uc: EndAgentSessionUseCase,
    ) -> None:
        self._start_uc = start_uc
        self._conduire_uc = conduire_uc
        self._end_uc = end_uc

    async def demarrer_session(self, session_id: SessionID) -> None:
        await self._start_uc.executer(session_id)

    async def traiter_reponse(self, session_id: SessionID, texte_reponse: str) -> tuple[str, bool]:
        return await self._conduire_uc.traiter_reponse_candidat(session_id, texte_reponse)

    async def terminer_session(self, session_id: SessionID) -> None:
        await self._end_uc.executer(session_id)