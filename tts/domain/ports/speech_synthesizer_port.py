
from typing import AsyncIterator, Protocol


class SpeechSynthesizerPort(Protocol):
    def synthetiser(self, texte: str, voice: str) -> AsyncIterator[bytes]:
        ...