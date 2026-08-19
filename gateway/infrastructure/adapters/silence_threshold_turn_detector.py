from datetime import datetime

from shared.domain import AudioChunk


class SilenceThresholdTurnDetector:

    def __init__(self, seuil_silence_ms: int = 2500) -> None:
        # Augmenté à 2500 ms (2.5 secondes) pour te laisser le temps de réfléchir
        self.seuil_silence_ms = seuil_silence_ms
        self._debut_silence: datetime | None = None

    def analyser(self, chunk: AudioChunk, silence_detecte: bool) -> bool:
        if not silence_detecte:
            self._debut_silence = None
            return False

        if self._debut_silence is None:
            self._debut_silence = chunk.captured_at
            return False

        duree_ms = (chunk.captured_at - self._debut_silence).total_seconds() * 1000
        
        if duree_ms >= self.seuil_silence_ms:
            # IMPORTANT : Remet à zéro pour ne pas redéclencher en boucle pendant les silences suivants
            self._debut_silence = None  
            return True

        return False