from gateway.domain.entities.entities import GatewaySession
from gateway.domain.ports.asr_client_port import ASRClientPort
from gateway.domain.ports.tts_client_port import TTSClientPort
from gateway.domain.ports.agent_client_port import AgentClientPort
from scoring.infrastructure.adapters.in_process_scoring_client import InProcessScoringClient


class CloseSessionUseCase:
    def __init__(
        self,
        asr_client: ASRClientPort,
        tts_client: TTSClientPort,
        agent_client: AgentClientPort,
        scoring_client: InProcessScoringClient,
    ) -> None:
        self._asr_client = asr_client
        self._tts_client = tts_client
        self._agent_client = agent_client
        self._scoring_client = scoring_client

    async def executer(self, session: GatewaySession, raison: str = "fin normale") -> None:
        await self._asr_client.terminer_session(session.session_id)
        await self._tts_client.terminer_session(session.session_id)
        await self._agent_client.terminer_session(session.session_id)

        rapport = await self._scoring_client.cloturer_session(session.session_id)
        print(f"[RAPPORT FINAL] session={session.session_id} score_global={rapport.score_global:.2f} nb_evaluations={len(rapport.evaluations)}")

        session.fermer()
        return rapport