from tts.infrastructure.adapters.session_registry import TTSSessionRegistry
from tts.infrastructure.adapters.piper_speech_synthesizer import PiperSpeechSynthesizer
from tts.application.use_cases.start_session import StartTTSSessionUseCase
from tts.application.use_cases.synthesize_text import SynthesizeTextUseCase
from tts.application.use_cases.end_session import EndTTSSessionUseCase


class TTSContainer:
    def __init__(self, voices_dir: str = ".") -> None:
        self.registry = TTSSessionRegistry()
        self.synthesizer = PiperSpeechSynthesizer(voices_dir=voices_dir)
        self.start_session = StartTTSSessionUseCase(self.registry)
        self.synthesize_text = SynthesizeTextUseCase(self.synthesizer, self.registry)
        self.end_session = EndTTSSessionUseCase(self.registry)