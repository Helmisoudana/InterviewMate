from gateway.domain.entities.entities import GatewaySession
from gateway.domain.ports.agent_client_port import AgentClientPort
from gateway.domain.ports.audio_broadcaster_port import AudioBroadcasterPort
from gateway.application.use_cases.request_voice_response import RequestVoiceResponseUseCase


class HandleTranscriptionResultUseCase:
    def __init__(self, agent_client: AgentClientPort, request_voice: RequestVoiceResponseUseCase) -> None:
        self._agent_client = agent_client
        self._request_voice = request_voice

    async def executer(self, session: GatewaySession, texte_final: str, broadcaster: AudioBroadcasterPort) -> None:
        question, est_termine = await self._agent_client.traiter_reponse(session.session_id, texte_final)

        if est_termine:
            session.fermer()
            return

        await self._request_voice.executer(session, question, broadcaster=broadcaster)