
from typing import List

from  domain.value_objects.session_id import SessionId as ASRSessionId
from  domain.value_objects.audio_chunk import AudioChunk as ASRAudioChunk
from  domain.value_objects.transcription_result import TranscriptionResult as ASRTranscriptionResult

from  application.use_cases.start_session import StartASRSessionUseCase
from  application.use_cases.process_audio_chunk import ProcessAudioChunkUseCase
from  application.use_cases.finalize_turn import FinalizeTurnUseCase
from  application.use_cases.end_session import EndASRSessionUseCase
from  infrastructure.adapters.session_registry import ASRSessionRegistry


class ASRGatewayEngineAdapter:
   

    def __init__(self, registry: ASRSessionRegistry, recognizer) -> None:
        self._registry = registry
        self._start = StartASRSessionUseCase()
        self._process = ProcessAudioChunkUseCase(recognizer)
        self._finalize = FinalizeTurnUseCase(recognizer)
        self._end = EndASRSessionUseCase()

    async def demarrer_session(self, session_id, language: str) -> None:
        asr_session_id = ASRSessionId(session_id.value)
        session = self._start.executer(asr_session_id, language)
        self._registry.enregistrer(session)

    async def traiter_chunk(self, session_id, chunk) -> List:
        session = self._obtenir_session(session_id)
        asr_chunk = ASRAudioChunk(data=chunk.data, sequence_number=chunk.sequence_number)
        resultat = await self._process.executer(session, asr_chunk)
        return [resultat]

    async def finaliser(self, session_id) -> ASRTranscriptionResult:
        session = self._obtenir_session(session_id)
        return await self._finalize.executer(session)

    async def terminer_session(self, session_id) -> None:
        session = self._obtenir_session(session_id)
        self._end.executer(session)
        self._registry.retirer(ASRSessionId(session_id.value))

    def _obtenir_session(self, session_id):
        asr_session_id = ASRSessionId(session_id.value)
        session = self._registry.obtenir(asr_session_id)
        if session is None:
            raise ValueError(f"Session ASR inconnue : {session_id.value}")
        return session