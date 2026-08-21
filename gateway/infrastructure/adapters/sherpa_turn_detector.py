from shared.domain import AudioChunk
from gateway.domain.ports.turn_detector_port import TurnDetectorPort
from gateway.domain.ports.asr_client_port import ASRClientPort


class SherpaTurnDetectorAdapter(TurnDetectorPort):
   

    def __init__(self, asr_client: ASRClientPort) -> None:
        self._asr_client = asr_client

    def analyser(self, chunk: AudioChunk, silence_detecte: bool) -> bool:

        return self._asr_client.est_fin_de_parole_detectee(chunk.session_id)
