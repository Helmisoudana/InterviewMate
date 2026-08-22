from typing import Optional
from gateway.domain.entities.entities import GatewaySession
from gateway.domain.ports.asr_client_port import ASRClientPort
from gateway.domain.ports.tts_client_port import TTSClientPort
from gateway.domain.ports.agent_client_port import AgentClientPort
from gateway.domain.ports.storage_client_port import StorageClientPort


class CloseSessionUseCase:
    def __init__(
        self,
        asr_client: ASRClientPort,
        tts_client: TTSClientPort,
        agent_client: AgentClientPort,
        storage_client: Optional[StorageClientPort] = None,
        scoring_client: Optional[object] = None,
    ) -> None:
        self._asr_client = asr_client
        self._tts_client = tts_client
        self._agent_client = agent_client
        self._storage_client = storage_client
        self._scoring_client = scoring_client

    async def executer(self, session: GatewaySession, raison: str = "fin normale"):
        await self._asr_client.terminer_session(session.session_id)
        await self._tts_client.terminer_session(session.session_id)
        await self._agent_client.terminer_session(session.session_id)

        # Passage du statut de l'entretien à TERMINE, via le client storage
        # (meme pattern que asr_client/tts_client/agent_client, plus de storage_repository direct)
        if self._storage_client:
            await self._storage_client.terminer_session(session.session_id)

        rapport = None
        if self._scoring_client:
            rapport = await self._scoring_client.cloturer_session(session.session_id)
            print(
                f"[RAPPORT FINAL] session={session.session_id} "
                f"score_global={rapport.score_global:.2f} "
                f"nb_evaluations={len(rapport.evaluations)}"
            )

        session.fermer()
        return rapport