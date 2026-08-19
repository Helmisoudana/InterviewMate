from gateway.domain.entities.entities import GatewaySession
from gateway.domain.ports.tts_client_port import TTSClientPort
from gateway.domain.ports.audio_broadcaster_port import AudioBroadcasterPort
from shared.domain import AudioChunk


class RequestVoiceResponseUseCase:

    def __init__(self, tts_client: TTSClientPort) -> None:
        self._tts_client = tts_client

    async def executer(self, session: GatewaySession, texte_a_dire: str, broadcaster: AudioBroadcasterPort) -> None:
        session.marquer_parole()
        async for chunk in self._tts_client.synthetiser_stream(session.session_id, texte_a_dire):
            await broadcaster.envoyer_audio_candidat(session.session_id, chunk)

        session.marquer_silence()