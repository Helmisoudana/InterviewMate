from typing import Protocol

from domain.value_objects.audio_chunk import AudioChunk


class TurnDetectorPort(Protocol):
    def analyser(self, chunk: AudioChunk, silence_detecte: bool) -> bool: ...