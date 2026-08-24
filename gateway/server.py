from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
import websockets

# --- Module Storage ---
from storage.infrastructure.adapters.postgres_storage_repository import PostgresStorageRepository
from storage.application.use_cases.save_latest_exchange import SaveLatestExchangeUseCase
from storage.application.use_cases.start_session import StartStorageSessionUseCase
from storage.application.use_cases.end_session import EndStorageSessionUseCase
from storage.application.use_cases.get_session_transcript import GetSessionTranscriptUseCase
from storage.application.use_cases.get_report import GetReportUseCase
from storage.application.use_cases.save_final_report import SaveFinalReportUseCase
from gateway.infrastructure.adapters.in_process_scoring_client import InProcessScoringClient
from scoring.infrastructure.adapters.groq_scorer_adapter import GroqScorerAdapter
from scoring.application.use_cases.generer_rapport_session import GenererRapportSessionUseCase
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

    def __init__(self) -> None:
        asr_repo = ASRSessionRegistry()
        recognizer = SherpaSpeechRecognizer(
            tokens="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/tokens.txt",
            encoder="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/encoder-epoch-29-avg-9-with-averaged-model.int8.onnx",
            decoder="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/decoder-epoch-29-avg-9-with-averaged-model.onnx",
            joiner="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/joiner-epoch-29-avg-9-with-averaged-model.int8.onnx",
            num_threads=2,
            provider="cpu",
            enable_endpoint_detection=True,
            rule1_min_trailing_silence=4.0,
            rule2_min_trailing_silence=3.0,
            rule3_min_utterance_length=120.0,
        )
        self.asr_client = InProcessASRClient(
            StartASRSessionUseCase(asr_repo),
            ProcessAudioChunkUseCase(recognizer, asr_repo, intervalle_chunks=1),
            FinalizeTurnUseCase(recognizer, asr_repo),
            EndASRSessionUseCase(asr_repo),
            CheckEndpointUseCase(recognizer),
        )

        tts_repo = TTSSessionRegistry()
        synthesizer = PiperSpeechSynthesizer(voices_dir=".")
        self.tts_client = InProcessTTSClient(
            StartTTSSessionUseCase(tts_repo),
            SynthesizeTextUseCase(synthesizer, tts_repo),
            EndTTSSessionUseCase(tts_repo),
        )

        # --- Module Storage : cree en premier, car agent (notifier) et scoring en dependent ---
        self.storage_repo = PostgresStorageRepository.creer_depuis_env()
        self.save_latest_exchange_uc = SaveLatestExchangeUseCase(repository=self.storage_repo)

        # --- Module Agent : notifier cable pour que chaque echange soit sauvegarde en storage ---
        agent_registry = AgentSessionRegistry()
        llm = OllamaAdapter(model="llama3:latest")
        notifier = StorageNotifierAdapter(self.save_latest_exchange_uc)
        self.agent_client = InProcessAgentClient(
            StartAgentSessionUseCase(llm, agent_registry),
            ConduireEntretienUseCase(llm, agent_registry, notifier),
            EndAgentSessionUseCase(agent_registry),
        )

        session_store = InMemorySessionStore()
        self.session_client = InProcessSessionClient(
            CreateSessionUseCase(session_store),
            GetSessionStateUseCase(session_store),
            session_store,
        )

        self.gateway_registry = SessionRegistry()

        storage_client = InProcessStorageClient(
            StartStorageSessionUseCase(self.storage_repo),
            EndStorageSessionUseCase(self.storage_repo),
        )
        self.storage_client = storage_client

        # --- Câblage du module Scoring ---
        llm_scorer = GroqScorerAdapter()
        generer_rapport_uc = GenererRapportSessionUseCase(
            llm_scorer=llm_scorer,
            get_transcript_uc=GetSessionTranscriptUseCase(self.storage_repo),
            get_report_uc=GetReportUseCase(self.storage_repo),
            save_report_uc=SaveFinalReportUseCase(self.storage_repo),
        )
        scoring_client = InProcessScoringClient(generer_rapport_uc)
        self.scoring_client = scoring_client

        # --- Assemblage des cas d'usage Gateway ---
        self.start_session_uc = StartSessionUseCase(
            self.session_client, self.asr_client, self.tts_client, self.agent_client,
            storage_client=storage_client,
        )
        self.receive_chunk_uc = ReceiveAudioChunkUseCase(self.asr_client, SherpaTurnDetectorAdapter(self.asr_client))
        self.request_voice_uc = RequestVoiceResponseUseCase(self.tts_client)
        self.handle_transcription_uc = HandleTranscriptionResultUseCase(
            self.agent_client, self.request_voice_uc
        )
        self.signal_disconnection_uc = SignalDisconnectionUseCase(self.session_client)
        self.request_reconnection_uc = RequestReconnectionUseCase(self.session_client)
        self.close_session_uc = CloseSessionUseCase(
            self.asr_client,
            self.tts_client,
            self.agent_client,
            storage_client=storage_client,
            scoring_client=scoring_client,
        )

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
    container = ApplicationContainer()

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