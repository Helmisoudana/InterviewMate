
from asr.domain.value_objects.transcription_result import TranscriptionResult


class WhisperSpeechRecognizer:
    def __init__(self, model_name: str = "base") -> None:
        # TODO: charger le modèle ici (ex: WhisperModel(model_name))
        self._model_name = model_name

    async def transcrire_partiel(self, audio_buffer: bytes, language: str) -> TranscriptionResult:
        # TODO: appeler le modèle sur le buffer accumulé jusqu'ici
        raise NotImplementedError("Brancher le vrai modèle ici")

    async def transcrire_final(self, audio_buffer: bytes, language: str) -> TranscriptionResult:
        # TODO: appeler le modèle en mode "transcription complète"
        raise NotImplementedError("Brancher le vrai modèle ici")