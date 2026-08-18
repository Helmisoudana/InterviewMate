from typing import Protocol

from shared.domain import AudioChunk


class TurnDetectorPort(Protocol):
    def analyser(self, chunk: AudioChunk, silence_detecte: bool) -> bool: ...