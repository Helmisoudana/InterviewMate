from typing import AsyncIterator

from domain.entities.tts_session import TTSSession
from domain.ports.speech_synthesizer_port import SpeechSynthesizerPort


class SynthesizeTextUseCase:
    def __init__(self, synthesizer: SpeechSynthesizerPort) -> None:
        self._synthesizer = synthesizer

    def executer(self, session: TTSSession, texte: str) -> AsyncIterator[bytes]:
        return self._synthesizer.synthetiser(texte, session.voice)