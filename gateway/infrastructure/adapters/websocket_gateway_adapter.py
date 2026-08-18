import asyncio
import json
import logging

import websockets
from websockets.server import WebSocketServerProtocol

from domain.entities.entities import GatewaySession, SessionFermeeError, SessionNonActiveError
from domain.value_objects.session_id import SessionId
from domain.value_objects.audio_chunk import AudioChunk
from domain.ports.audio_broadcaster_port import AudioBroadcasterPort
from domain.ports.asr_client_port import ASRClientPort

from application.use_cases.start_session import StartSessionUseCase, SessionInvalideError
from application.use_cases.receive_audio_chunk import ReceiveAudioChunkUseCase
from application.use_cases.request_voice_response import RequestVoiceResponseUseCase
from application.use_cases.signal_disconnection import SignalDisconnectionUseCase
from application.use_cases.request_reconnection import RequestReconnectionUseCase
from application.use_cases.close_session import CloseSessionUseCase
from application.use_cases.handle_transcription_result import HandleTranscriptionResultUseCase

from infrastructure.adapters.simple_vad import is_silence
from infrastructure.adapters.session_registry import SessionRegistry

logger = logging.getLogger(__name__)


class WebSocketConnectionHandler(AudioBroadcasterPort):
    """Une instance par connexion active. Implémente AudioBroadcasterPort
    pour pouvoir renvoyer l'audio TTS au candidat via ce même canal."""

    def __init__(
        self,
        websocket: WebSocketServerProtocol,
        registry: SessionRegistry,
        asr_client: ASRClientPort,
        start_session: StartSessionUseCase,
        receive_chunk: ReceiveAudioChunkUseCase,
        request_voice: RequestVoiceResponseUseCase,
        signal_disconnection: SignalDisconnectionUseCase,
        request_reconnection: RequestReconnectionUseCase,
        close_session: CloseSessionUseCase,
        handle_transcription: HandleTranscriptionResultUseCase,
    ) -> None:
        self._ws = websocket
        self._registry = registry
        self._asr_client = asr_client
        self._start_session = start_session
        self._receive_chunk = receive_chunk
        self._request_voice = request_voice
        self._signal_disconnection = signal_disconnection
        self._request_reconnection = request_reconnection
        self._close_session = close_session
        self._handle_transcription = handle_transcription
        self._session: GatewaySession | None = None
        self._sequence = 0

    # ---- Implémentation du port sortant AudioBroadcasterPort ----------

    async def envoyer_audio_candidat(self, session_id: SessionId, chunk: AudioChunk) -> None:
        await self._ws.send(chunk.data)


    async def gerer_connexion(self) -> None:
        try:
            message_init = await asyncio.wait_for(self._ws.recv(), timeout=10)
            init = json.loads(message_init)
            session_id = SessionId(init["session_id"])
        except (asyncio.TimeoutError, json.JSONDecodeError, KeyError, ValueError):
            await self._ws.close(code=4000, reason="message d'initialisation invalide")
            return

        est_reconnexion = init.get("reconnect", False)

        if est_reconnexion:
            await self._gerer_reconnexion(session_id)
        else:
            await self._gerer_nouvelle_session(session_id)

        if self._session is None:
            return  

        self._registry.enregistrer(session_id, self._session, self)

        try:
            async for message in self._ws:
                await self._traiter_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning("Connexion perdue pour %s : %s", session_id.value, e)
            await self._signal_disconnection.executer(self._session, raison=str(e))
        finally:
            self._registry.retirer(session_id)


    async def _gerer_nouvelle_session(self, session_id: SessionId) -> None:
        self._session = GatewaySession(session_id)
        try:
            await self._start_session.executer(self._session)
            self._asr_client.souscrire_resultats(session_id, self._traiter_resultat_asr)
        except SessionInvalideError as e:
            await self._ws.close(code=4001, reason=str(e))
            self._session = None
            return
        await self._ws.send(json.dumps({"type": "session_ready"}))

    async def _gerer_reconnexion(self, session_id: SessionId) -> None:
        existante = self._registry.obtenir(session_id)
        if existante is None:
            await self._ws.close(code=4004, reason="aucune session à reconnecter")
            return
        self._session = existante.session
        try:
            await self._request_reconnection.executer(self._session)
        except SessionFermeeError as e:
            await self._ws.close(code=4001, reason=str(e))
            self._session = None
            return
        await self._ws.send(json.dumps({"type": "reconnected"}))

    async def _traiter_message(self, message) -> None:
        if isinstance(message, bytes):
            await self._traiter_chunk_audio(message)
        else:
            await self._traiter_message_controle(json.loads(message))

    async def _traiter_chunk_audio(self, data: bytes) -> None:
        self._sequence += 1
        chunk = AudioChunk(data=data, sequence_number=self._sequence)
        silence = is_silence(data)
        try:
            await self._receive_chunk.executer(self._session, chunk, silence_detecte=silence)
        except SessionNonActiveError as e:
            logger.warning("Chunk ignoré : %s", e)

    async def _traiter_message_controle(self, payload: dict) -> None:
        if payload.get("type") == "close":
            await self._close_session.executer(self._session, raison="fermeture demandée par le client")
            await self._ws.close(code=1000)

    async def _traiter_resultat_asr(self, resultat) -> None:
        if resultat.type != "final":
            return
        await self._handle_transcription.executer(self._session, resultat.text, broadcaster=self)