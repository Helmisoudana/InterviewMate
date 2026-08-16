from domain.entities.entities import GatewaySession, SessionNonActiveError
from domain.ports.tts_client_port import TTSClientPort
from domain.ports.audio_broadcaster_port import AudioBroadcasterPort
from domain.value_objects.audio_chunk import AudioChunk


class RequestVoiceResponseUseCase:
    def __init__(self, tts_client: TTSClientPort) -> None:
        self._tts_client = tts_client

    async def executer(self, session: GatewaySession, texte: str, broadcaster: AudioBroadcasterPort) -> None:
        if not session.est_active():
            raise SessionNonActiveError(f"Session {session.session_id.value} non active")

        sequence = 0
        async for audio_bytes in self._tts_client.synthetiser_stream(session.session_id, texte):
            sequence += 1
            chunk = AudioChunk(data=audio_bytes, sequence_number=sequence)
            await broadcaster.envoyer_audio_candidat(session.session_id, chunk)