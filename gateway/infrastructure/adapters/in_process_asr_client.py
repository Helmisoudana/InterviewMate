from domain.ports.asr_client_port import ResultCallback
from domain.value_objects.session_id import SessionId
from domain.value_objects.audio_chunk import AudioChunk


class InProcessASRClient:

    def __init__(self, engine) -> None:
        self._engine = engine
        self._callbacks: dict[str, ResultCallback] = {}

    def souscrire_resultats(self, session_id: SessionId, callback: ResultCallback) -> None:
        self._callbacks[session_id.value] = callback

    async def demarrer_session(self, session_id: SessionId, language: str) -> None:
        await self._engine.demarrer_session(session_id, language)

    async def envoyer_chunk(self, session_id: SessionId, chunk: AudioChunk) -> None:
        resultats = await self._engine.traiter_chunk(session_id, chunk)
        callback = self._callbacks.get(session_id.value)
        if callback is None:
            return
        for resultat in resultats:
            await callback(resultat)

    async def signaler_fin_de_tour(self, session_id: SessionId) -> None:
        resultat_final = await self._engine.finaliser(session_id)
        callback = self._callbacks.get(session_id.value)
        if callback is not None:
            await callback(resultat_final)

    async def terminer_session(self, session_id: SessionId) -> None:
        await self._engine.terminer_session(session_id)
        self._callbacks.pop(session_id.value, None)