from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
import websockets

from shared.domain.value_objects import SessionID

# --- Module Storage ---
from storage.infrastructure.adapters.postgres_storage_repository import PostgresStorageRepository
from storage.application.use_cases.save_latest_exchange import SaveLatestExchangeUseCase
from storage.application.use_cases.start_session import StartStorageSessionUseCase
from storage.application.use_cases.end_session import EndStorageSessionUseCase
from gateway.infrastructure.adapters.in_process_storage_client import InProcessStorageClient

# --- Module ASR ---
from asr.infrastructure.adapters.session_registry import ASRSessionRegistry
from asr.infrastructure.adapters.sherpa_speech_recognizer import SherpaSpeechRecognizer
from asr.application.use_cases.start_session import StartASRSessionUseCase
from asr.application.use_cases.process_audio_chunk import ProcessAudioChunkUseCase
from asr.application.use_cases.finalize_turn import FinalizeTurnUseCase
from asr.application.use_cases.end_session import EndASRSessionUseCase
from asr.application.use_cases.check_endpoint import CheckEndpointUseCase
from gateway.infrastructure.adapters.in_process_asr_client import InProcessASRClient

# --- Module TTS ---
from tts.infrastructure.adapters.session_registry import TTSSessionRegistry
from tts.infrastructure.adapters.piper_speech_synthesizer import PiperSpeechSynthesizer
from tts.application.use_cases.start_session import StartTTSSessionUseCase
from tts.application.use_cases.synthesize_text import SynthesizeTextUseCase
from tts.application.use_cases.end_session import EndTTSSessionUseCase
from gateway.infrastructure.adapters.in_process_tts_client import InProcessTTSClient

# --- Module Agent ---
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry
from agent.infrastructure.adapters.ollama_adapter import OllamaAdapter
from agent.infrastructure.adapters.storage_notifier_adapter import StorageNotifierAdapter
from agent.infrastructure.fakes.fake_session_repository_adapter import FakeSessionRepositoryAdapter
from agent.application.use_cases.start_session import StartAgentSessionUseCase
from agent.application.use_cases.conduire_entretien import ConduireEntretienUseCase
from agent.application.use_cases.end_session import EndAgentSessionUseCase
from gateway.infrastructure.adapters.in_process_agent_client import InProcessAgentClient

# --- Module Session ---
from session.infrastructure.adapters.in_memory_session_store import InMemorySessionStore
from session.application.use_cases.create_session import CreateSessionUseCase
from session.application.use_cases.get_session_state import GetSessionStateUseCase
from gateway.infrastructure.adapters.in_process_session_client import InProcessSessionClient

# --- Module Gateway ---
from gateway.application.use_cases.start_session import StartSessionUseCase
from gateway.application.use_cases.receive_audio_chunk import ReceiveAudioChunkUseCase
from gateway.application.use_cases.request_voice_response import RequestVoiceResponseUseCase
from gateway.application.use_cases.handle_transcription_result import HandleTranscriptionResultUseCase
from gateway.application.use_cases.signal_disconnection import SignalDisconnectionUseCase
from gateway.application.use_cases.request_reconnection import RequestReconnectionUseCase
from gateway.application.use_cases.close_session import CloseSessionUseCase
from gateway.infrastructure.adapters.session_registry import SessionRegistry
from gateway.infrastructure.adapters.websocket_gateway_adapter import WebSocketConnectionHandler
from gateway.infrastructure.adapters.sherpa_turn_detector import SherpaTurnDetectorAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway.server")


class ApplicationContainer:
    """
    Composition root. Construction en une seule factory asynchrone `creer()` :
    chaque module (storage, asr, tts, agent, session, gateway) est câblé au même
    niveau, dans le même bloc — storage n'est pas un cas particulier, juste le
    seul module dont la construction du repository est async (connexion Postgres).
    """

    def __init__(self) -> None:
        # Attributs peuplés par la factory asynchrone `creer()`.
        self.storage_repo = None
        self.save_latest_exchange_uc: SaveLatestExchangeUseCase | None = None
        self.asr_client = None
        self.tts_client = None
        self.agent_client = None
        self.session_client = None
        self.gateway_registry = None
        self.start_session_uc = None
        self.receive_chunk_uc = None
        self.request_voice_uc = None
        self.handle_transcription_uc = None
        self.signal_disconnection_uc = None
        self.request_reconnection_uc = None
        self.close_session_uc = None

    @classmethod
    async def creer(cls) -> "ApplicationContainer":
        """Assemble tous les modules et retourne un container prêt à l'emploi."""
        container = cls()

        # --- Storage : même famille que les autres modules, juste une ligne async ---
        container.storage_repo = await PostgresStorageRepository.creer_depuis_env()
        container.save_latest_exchange_uc = SaveLatestExchangeUseCase(repository=container.storage_repo)
        storage_client = InProcessStorageClient(
            StartStorageSessionUseCase(container.storage_repo),
            EndStorageSessionUseCase(container.storage_repo),
        )

        # --- ASR ---
        asr_repo = ASRSessionRegistry()
        recognizer = SherpaSpeechRecognizer(
            tokens="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/tokens.txt",
            encoder="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/encoder-epoch-29-avg-9-with-averaged-model.int8.onnx",
            decoder="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/decoder-epoch-29-avg-9-with-averaged-model.onnx",
            joiner="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/joiner-epoch-29-avg-9-with-averaged-model.int8.onnx",
            num_threads=2,
            provider="cuda",
            enable_endpoint_detection=True,
            rule1_min_trailing_silence=4.0,
            rule2_min_trailing_silence=3.0,
            rule3_min_utterance_length=120.0,
        )
        container.asr_client = InProcessASRClient(
            StartASRSessionUseCase(asr_repo),
            ProcessAudioChunkUseCase(recognizer, asr_repo, intervalle_chunks=1),
            FinalizeTurnUseCase(recognizer, asr_repo),
            EndASRSessionUseCase(asr_repo),
            CheckEndpointUseCase(recognizer),
        )

        # --- TTS ---
        tts_repo = TTSSessionRegistry()
        synthesizer = PiperSpeechSynthesizer(voices_dir=".")
        container.tts_client = InProcessTTSClient(
            StartTTSSessionUseCase(tts_repo),
            SynthesizeTextUseCase(synthesizer, tts_repo),
            EndTTSSessionUseCase(tts_repo),
        )

        # --- Agent (dépend de storage pour son notifier) ---
        agent_repo = FakeSessionRepositoryAdapter()
        agent_registry = AgentSessionRegistry()
        llm = OllamaAdapter(model="llama3:latest", keep_alive="30m")
        notifier = StorageNotifierAdapter(container.save_latest_exchange_uc)
        container.agent_client = InProcessAgentClient(
            StartAgentSessionUseCase(agent_repo, agent_registry),
            ConduireEntretienUseCase(llm, agent_repo, notifier, agent_registry),
            EndAgentSessionUseCase(agent_registry),
        )

        # --- Session ---
        session_store = InMemorySessionStore()
        container.session_client = InProcessSessionClient(
            CreateSessionUseCase(session_store),
            GetSessionStateUseCase(session_store),
            session_store,
        )

        container.gateway_registry = SessionRegistry()

        # --- Gateway : assemblage final des use cases, tous les clients étant prêts ---
        container.start_session_uc = StartSessionUseCase(
            container.session_client, container.asr_client, container.tts_client, container.agent_client,
            storage_client=storage_client,
        )
        container.receive_chunk_uc = ReceiveAudioChunkUseCase(
            container.asr_client, SherpaTurnDetectorAdapter(container.asr_client)
        )
        container.request_voice_uc = RequestVoiceResponseUseCase(container.tts_client)
        container.handle_transcription_uc = HandleTranscriptionResultUseCase(
            container.agent_client, container.request_voice_uc
        )
        container.signal_disconnection_uc = SignalDisconnectionUseCase(container.session_client)
        container.request_reconnection_uc = RequestReconnectionUseCase(container.session_client)
        container.close_session_uc = CloseSessionUseCase(
            container.asr_client, container.tts_client, container.agent_client,
            storage_client=storage_client,
        )

        return container

    async def close(self) -> None:
        if self.storage_repo:
            await self.storage_repo.fermer()


async def handler_factory(container: ApplicationContainer, websocket) -> None:
    handler = WebSocketConnectionHandler(
        websocket=websocket,
        registry=container.gateway_registry,
        asr_client=container.asr_client,
        start_session=container.start_session_uc,
        receive_chunk=container.receive_chunk_uc,
        request_voice=container.request_voice_uc,
        signal_disconnection=container.signal_disconnection_uc,
        request_reconnection=container.request_reconnection_uc,
        close_session=container.close_session_uc,
        handle_transcription=container.handle_transcription_uc,
    )
    await handler.gerer_connexion()


async def main(host: str = "0.0.0.0", port: int = 8765) -> None:
    logger.info("Chargement des modèles (Sherpa / Piper / Ollama)...")
    container = await ApplicationContainer.creer()

    async def routed_handler(websocket):
        await handler_factory(container, websocket)

    logger.info("Serveur WebSocket démarré sur ws://%s:%s", host, port)
    try:
        async with websockets.serve(
            routed_handler,
            host,
            port,
            ping_interval=30,
        ):
            await asyncio.Future()
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())