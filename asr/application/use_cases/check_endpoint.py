from shared.domain import SessionID
from asr.domain.ports.speech_recognizer_port import SpeechRecognizerPort


class CheckEndpointUseCase:
    """Expose l'endpointing natif du moteur ASR (ex: sherpa) au reste de l'application."""

    def __init__(self, recognizer: SpeechRecognizerPort) -> None:
        self._recognizer = recognizer

    def executer(self, session_id: SessionID) -> bool:
        return self._recognizer.est_fin_de_parole_detectee(session_id)
