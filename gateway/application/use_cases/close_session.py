from domain.entities.entities import GatewaySession
from domain.ports.asr_client_port import ASRClientPort
from domain.ports.tts_client_port import TTSClientPort
from domain.ports.agent_client_port import AgentClientPort


class CloseSessionUseCase:
    def __init__(self, asr_client: ASRClientPort, tts_client: TTSClientPort, agent_client : AgentClientPort) -> None:
        self._asr_client = asr_client
        self._tts_client = tts_client
        self.agent_client = AgentClientPort

    async def executer(self, session: GatewaySession, raison: str = "fin normale") -> None:
        await self._asr_client.terminer_session(session.session_id)
        await self._tts_client.terminer_session(session.session_id)
        await self.agent_client.terminer_session(session.session_id)
        session.fermer()