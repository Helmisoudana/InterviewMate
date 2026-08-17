
from typing import Protocol

from  domain.value_objects.transcription_result import TranscriptionResult


class SpeechRecognizerPort(Protocol):
    async def transcrire_partiel(self, audio_buffer: bytes, language: str) -> TranscriptionResult:
        ...

    async def transcrire_final(self, audio_buffer: bytes, language: str) -> TranscriptionResult:
        ...
        