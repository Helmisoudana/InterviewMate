from typing import AsyncIterator

from  domain.value_objects.session_id import SessionId
from  infrastructure.engines.tts_engine import TTSEngine


class InProcessTTSClient:
    """Implémente TTSClientPort en appelant directement un TTSEngine, sans réseau."""

    def __init__(self, engine: TTSEngine) -> None:
        self._engine = engine

    def synthetiser_stream(self, session_id: SessionId, texte: str) -> AsyncIterator[bytes]:
        return self._engine.synthetiser(session_id, texte)