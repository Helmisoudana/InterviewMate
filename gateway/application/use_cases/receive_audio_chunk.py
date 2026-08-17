from domain.entities.entities import GatewaySession
from domain.value_objects.audio_chunk import AudioChunk
from domain.ports.asr_client_port import ASRClientPort
from domain.ports.turn_detector_port import TurnDetectorPort


class ReceiveAudioChunkUseCase:
    def __init__(self, asr_client: ASRClientPort, turn_detector: TurnDetectorPort) -> None:
        self._asr_client = asr_client
        self._turn_detector = turn_detector

    async def executer(self, session: GatewaySession, chunk: AudioChunk, silence_detecte: bool) -> None:
        if silence_detecte:
            session.marquer_silence()
        else:
            session.marquer_parole()

        await self._asr_client.envoyer_chunk(session.session_id, chunk)

        if self._turn_detector.analyser(chunk, silence_detecte):
            session.marquer_fin_de_tour()
            await self._asr_client.signaler_fin_de_tour(session.session_id)