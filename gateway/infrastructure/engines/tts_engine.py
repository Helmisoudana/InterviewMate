from typing import AsyncIterator, Protocol

from domain.value_objects.session_id import SessionId


class TTSEngine(Protocol):
    """C'est CETTE interface que tu implémentes avec ton vrai moteur de synthèse."""

    def synthetiser(self, session_id: SessionId, texte: str) -> AsyncIterator[bytes]:
        """Doit yield des chunks audio au fur et à mesure, sans attendre la fin."""
        ...