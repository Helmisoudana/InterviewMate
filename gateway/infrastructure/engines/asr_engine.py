from typing import List, Protocol

from  domain.value_objects.session_id import SessionId
from  domain.value_objects.audio_chunk import AudioChunk
from  domain.value_objects.transcription_result import TranscriptionResult


class ASREngine(Protocol):
    """C'est CETTE interface que tu implémentes avec ton vrai modèle ASR."""

    async def demarrer_session(self, session_id: SessionId, language: str) -> None:
        """Initialise l'état interne du moteur pour cette session (buffer, contexte...)."""
        ...

    async def traiter_chunk(self, session_id: SessionId, chunk: AudioChunk) -> List[TranscriptionResult]:
        """Retourne 0, 1 ou plusieurs résultats partiels générés par ce chunk."""
        ...

    async def finaliser(self, session_id: SessionId) -> TranscriptionResult:
        """Appelé à la fin d'un tour de parole. Doit retourner le résultat final."""
        ...

    async def terminer_session(self, session_id: SessionId) -> None:
        """Libère les ressources associées à la session."""
        ...