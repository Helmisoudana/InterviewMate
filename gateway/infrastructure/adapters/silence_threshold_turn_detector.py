from datetime import datetime

from shared.domain import AudioChunk


class SilenceThresholdTurnDetector:

    def __init__(self, seuil_silence_ms: int = 1000) -> None:
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
        return duree_ms >= self.seuil_silence_ms