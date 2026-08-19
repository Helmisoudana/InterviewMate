from typing import AsyncIterator
from gateway.domain.ports.tts_client_port import TTSClientPort
from shared.domain import SessionID, AudioChunk
from tts.application.use_cases.start_session import StartTTSSessionUseCase
from tts.application.use_cases.synthesize_text import SynthesizeTextUseCase
from tts.application.use_cases.end_session import EndTTSSessionUseCase


class InProcessTTSClient(TTSClientPort):
    def __init__(
        self,
        start_uc: StartTTSSessionUseCase,
        synthesize_uc: SynthesizeTextUseCase,
        end_uc: EndTTSSessionUseCase,
    ) -> None:
        self._start_uc = start_uc
        self._synthesize_uc = synthesize_uc
        self._end_uc = end_uc

    async def demarrer_session(self, session_id: SessionID, voice: str) -> None:
        self._start_uc.executer(session_id, voice)

    def synthetiser_stream(self, session_id: SessionID, texte: str) -> AsyncIterator[AudioChunk]:
        return self._synthesize_uc.executer(session_id, texte)

    async def terminer_session(self, session_id: SessionID) -> None:
        self._end_uc.executer(session_id)