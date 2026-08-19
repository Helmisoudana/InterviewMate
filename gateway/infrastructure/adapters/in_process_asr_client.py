from gateway.domain.ports.asr_client_port import ResultCallback, ASRClientPort
from shared.domain import SessionID, AudioChunk
from asr.application.use_cases.start_session import StartASRSessionUseCase
from asr.application.use_cases.process_audio_chunk import ProcessAudioChunkUseCase
from asr.application.use_cases.finalize_turn import FinalizeTurnUseCase
from asr.application.use_cases.end_session import EndASRSessionUseCase


class InProcessASRClient(ASRClientPort):
    def __init__(
        self,
        start_uc: StartASRSessionUseCase,
        process_uc: ProcessAudioChunkUseCase,
        finalize_uc: FinalizeTurnUseCase,
        end_uc: EndASRSessionUseCase,
    ) -> None:
        self._start_uc = start_uc
        self._process_uc = process_uc
        self._finalize_uc = finalize_uc
        self._end_uc = end_uc
        self._callbacks: dict[str, ResultCallback] = {}

    def souscrire_resultats(self, session_id: SessionID, callback: ResultCallback) -> None:
        self._callbacks[session_id.value] = callback

    async def demarrer_session(self, session_id: SessionID, language: str) -> None:
        self._start_uc.executer(session_id, language)

    async def envoyer_chunk(self, session_id: SessionID, chunk: AudioChunk) -> None:
        resultat = await self._process_uc.executer(session_id, chunk)
        callback = self._callbacks.get(session_id.value)
        if callback is not None:
            await callback(resultat)

    async def signaler_fin_de_tour(self, session_id: SessionID) -> None:
        resultat_final = await self._finalize_uc.executer(session_id)
        callback = self._callbacks.get(session_id.value)
        if callback is not None:
            await callback(resultat_final)

    async def terminer_session(self, session_id: SessionID) -> None:
        self._end_uc.executer(session_id)
        self._callbacks.pop(session_id.value, None)