from infrastructure.adapters.session_registry import TTSSessionRegistry
from infrastructure.adapters.piper_speech_synthesizer import PiperSpeechSynthesizer
from infrastructure.adapters.gateway_engine_adapter import TTSGatewayEngineAdapter


def construire_tts_engine(voices_dir: str = ".") -> TTSGatewayEngineAdapter:
    registry = TTSSessionRegistry()
    synthesizer = PiperSpeechSynthesizer(voices_dir=voices_dir)
    return TTSGatewayEngineAdapter(registry=registry, synthesizer=synthesizer)