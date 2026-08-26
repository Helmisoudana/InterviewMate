import asyncio
import json
import logging

import websockets
from websockets.server import WebSocketServerProtocol

from gateway.domain.entities.entities import GatewaySession, SessionFermeeError, SessionNonActiveError
from shared.domain import SessionID
from shared.domain import AudioChunk
from gateway.domain.ports.audio_broadcaster_port import AudioBroadcasterPort
from gateway.domain.ports.asr_client_port import ASRClientPort

from agent.domain.value_objects.interview_phase import DureeEntretien, DifficultyLevel

from gateway.application.use_cases.start_session import StartSessionUseCase, SessionInvalideError
from gateway.application.use_cases.receive_audio_chunk import ReceiveAudioChunkUseCase
from gateway.application.use_cases.request_voice_response import RequestVoiceResponseUseCase
from gateway.application.use_cases.signal_disconnection import SignalDisconnectionUseCase
from gateway.application.use_cases.request_reconnection import RequestReconnectionUseCase
from gateway.application.use_cases.close_session import CloseSessionUseCase
from gateway.application.use_cases.handle_transcription_result import HandleTranscriptionResultUseCase

from gateway.infrastructure.adapters.session_registry import SessionRegistry

logger = logging.getLogger(__name__)


class WebSocketConnectionHandler(AudioBroadcasterPort):

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

        self._audio_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._consumer_task: asyncio.Task | None = None

    async def envoyer_audio_candidat(self, session_id: SessionID, chunk: AudioChunk) -> None:
        await self._ws.send(chunk.data)

    async def envoyer_texte(self, session_id: SessionID, type_message: str, texte: str) -> None:
        await self._ws.send(json.dumps({"type": type_message, "text": texte}))

    async def gerer_connexion(self) -> None:
        try:
            message_init = await asyncio.wait_for(self._ws.recv(), timeout=10)
            init = json.loads(message_init)
            session_id = SessionID(init["session_id"])
        except (asyncio.TimeoutError, json.JSONDecodeError, KeyError, ValueError):
            await self._ws.close(code=4000, reason="message d'initialisation invalide")
            return

        est_reconnexion = init.get("reconnect", False)
        config = init.get("config", {}) or {}

        if est_reconnexion:
            await self._gerer_reconnexion(session_id)
        else:
            await self._gerer_nouvelle_session(session_id, config)

        if self._session is None:
            return

        self._registry.enregistrer(session_id, self._session, self)

        self._consumer_task = asyncio.create_task(self._consommer_audio())

        try:
            async for message in self._ws:
                if isinstance(message, bytes):
                    await self._audio_queue.put(message)
                else:
                    await self._traiter_message_controle(json.loads(message))
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning("Connexion perdue pour %s : %s", session_id.value, e)
            await self._signal_disconnection.executer(self._session, raison=str(e))
        finally:
            self._consumer_task.cancel()
            self._registry.retirer(session_id)

    async def _consommer_audio(self) -> None:
        try:
            while True:
                data = await self._audio_queue.get()
                try:
                    await self._traiter_chunk_audio(data)
                except Exception:
                    logger.exception("Erreur lors du traitement d'un chunk audio")
        except asyncio.CancelledError:
            pass

    async def _gerer_nouvelle_session(self, session_id: SessionID, config: dict) -> None:
        self._session = GatewaySession(session_id)

        poste = config.get("poste") or "Poste non spécifié"
        langue = config.get("langue") or "fr"

        duree_raw = str(config.get("duree", "MOYENNE")).upper()
        try:
            duree = DureeEntretien[duree_raw]
        except KeyError:
            await self._ws.close(code=4002, reason=f"duree invalide: {duree_raw}")
            self._session = None
            return

        difficulte_raw = str(config.get("difficulte", "MOYEN")).upper()
        try:
            difficulte = DifficultyLevel[difficulte_raw]
        except KeyError:
            await self._ws.close(code=4002, reason=f"difficulte invalide: {difficulte_raw}")
            self._session = None
            return

        try:
            message_bienvenue = await self._start_session.executer(
                self._session,
                language=langue,
                poste=poste,
                duree=duree,
                difficulte=difficulte,
            )
            self._asr_client.souscrire_resultats(session_id, self._traiter_resultat_asr)
        except SessionInvalideError as e:
            await self._ws.close(code=4001, reason=str(e))
            self._session = None
            return

        await self._ws.send(json.dumps({"type": "session_ready"}))

        if message_bienvenue:
            await self.envoyer_texte(session_id, "agent_message", message_bienvenue)
            await self._request_voice.executer(self._session, message_bienvenue, broadcaster=self)

    async def _gerer_reconnexion(self, session_id: SessionID) -> None:
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

    async def _traiter_chunk_audio(self, data: bytes) -> None:
        if self._session is None:
            return

        self._sequence += 1
        chunk = AudioChunk(
            session_id=self._session.session_id,
            data=data,
            sequence_number=self._sequence
        )
        try:
            await self._receive_chunk.executer(self._session, chunk)
        except SessionNonActiveError as e:
            logger.warning("Chunk ignoré : %s", e)

    async def _traiter_message_controle(self, payload: dict) -> None:
        if payload.get("type") == "close":
            await self._close_session.executer(self._session, raison="fermeture demandée par le client")
            await self._ws.close(code=1000)

    async def _traiter_resultat_asr(self, resultat) -> None:
        if not resultat.is_final or self._session is None:
            return

        texte_propre = resultat.text.strip() if resultat.text else ""
        if not texte_propre:
            return

        await self.envoyer_texte(self._session.session_id, "transcription", texte_propre)
        await self._handle_transcription.executer(self._session, texte_propre, broadcaster=self)