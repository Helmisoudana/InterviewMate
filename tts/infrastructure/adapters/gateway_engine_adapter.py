
from typing import AsyncIterator

from domain.value_objects.session_id import SessionId as TTSSessionId
from application.use_cases.start_session import StartTTSSessionUseCase
from application.use_cases.synthesize_text import SynthesizeTextUseCase
from application.use_cases.end_session import EndTTSSessionUseCase
from infrastructure.adapters.session_registry import TTSSessionRegistry


class TTSGatewayEngineAdapter:
    def __init__(self, registry: TTSSessionRegistry, synthesizer) -> None:
        self._registry = registry
        self._start = StartTTSSessionUseCase()
        self._synthesize = SynthesizeTextUseCase(synthesizer)
        self._end = EndTTSSessionUseCase()

    async def demarrer_session(self, session_id, voice: str) -> None:
        tts_session_id = TTSSessionId(session_id.value)
        session = self._start.executer(tts_session_id, voice)
        self._registry.enregistrer(session)

    def synthetiser(self, session_id, texte: str) -> AsyncIterator[bytes]:
        session = self._obtenir_session(session_id)
        return self._synthesize.executer(session, texte)

    async def terminer_session(self, session_id) -> None:
        session = self._obtenir_session(session_id)
        self._end.executer(session)
        self._registry.retirer(TTSSessionId(session_id.value))

    def _obtenir_session(self, session_id):
        tts_session_id = TTSSessionId(session_id.value)
        session = self._registry.obtenir(tts_session_id)
        if session is None:
            raise ValueError(f"Session TTS inconnue : {session_id.value}")
        return session