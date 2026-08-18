from gateway.domain.entities.entities import GatewaySession
from gateway.domain.ports.agent_client_port import AgentClientPort
from gateway.domain.ports.tts_client_port import TTSClientPort
from gateway.domain.ports.audio_broadcaster_port import AudioBroadcasterPort
from shared.domain import AudioChunk


class RequestVoiceResponseUseCase:
    def __init__(self, agent_client: AgentClientPort, tts_client: TTSClientPort) -> None:
        self._agent_client = agent_client
        self._tts_client = tts_client

    async def executer(self, session: GatewaySession, texte_reponse: str, broadcaster: AudioBroadcasterPort) -> None:
        texte, termine = await self._agent_client.traiter_reponse(session.session_id, texte_reponse)

        if termine:
            session.marquer_fin_de_tour()
            return

        session.marquer_parole()
        async for chunk in self._tts_client.synthetiser_stream(session.session_id, texte):
            await broadcaster.envoyer_audio_candidat(session.session_id, chunk)

        session.marquer_silence()