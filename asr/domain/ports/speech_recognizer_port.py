from typing import Protocol
from shared.domain import SessionID, TranscriptionResult


class SpeechRecognizerPort(Protocol):
    async def transcrire_partiel(self, session_id: SessionID, audio_buffer: bytes, language: str) -> TranscriptionResult:
        ...

    async def transcrire_final(self, session_id: SessionID, audio_buffer: bytes, language: str) -> TranscriptionResult:
        ...

    def est_fin_de_parole_detectee(self, session_id: SessionID) -> bool:
        """Optionnel : uniquement implémenté par les moteurs ayant un VAD/endpointing natif (ex: sherpa)."""
        ...