# gateway/server.py
"""
Composition root RÉEL du backend : démarre le serveur WebSocket et câble
les vrais adapters (Whisper, Ollama, Piper) au lieu des fakes utilisées
par gateway/dev_runner.py.

Lancer depuis la racine du projet :
    python -m gateway.server
"""
import asyncio
import logging

import websockets

# ASR (réel : faster-whisper)
from asr.infrastructure.adapters.session_registry import ASRSessionRegistry
from asr.infrastructure.adapters.whisper_speech_recognizer import WhisperSpeechRecognizer
from asr.application.use_cases.start_session import StartASRSessionUseCase
from asr.application.use_cases.process_audio_chunk import ProcessAudioChunkUseCase
from asr.application.use_cases.finalize_turn import FinalizeTurnUseCase
from asr.application.use_cases.end_session import EndASRSessionUseCase
from gateway.infrastructure.adapters.in_process_asr_client import InProcessASRClient

# TTS (réel : Piper)
from tts.infrastructure.adapters.session_registry import TTSSessionRegistry
from tts.infrastructure.adapters.piper_speech_synthesizer import PiperSpeechSynthesizer
from tts.application.use_cases.start_session import StartTTSSessionUseCase
from tts.application.use_cases.synthesize_text import SynthesizeTextUseCase
from tts.application.use_cases.end_session import EndTTSSessionUseCase
from gateway.infrastructure.adapters.in_process_tts_client import InProcessTTSClient

# Agent (réel : Ollama)
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry
from agent.infrastructure.adapters.ollama_adapter import OllamaAdapter
from agent.infrastructure.fakes.fake_session_repository_adapter import FakeSessionRepositoryAdapter
from agent.infrastructure.fakes.fake_scoring_notifier_adapter import FakeScoringNotifierAdapter
from agent.application.use_cases.start_session import StartAgentSessionUseCase
from agent.application.use_cases.conduire_entretien import ConduireEntretienUseCase
from agent.application.use_cases.end_session import EndAgentSessionUseCase
from gateway.infrastructure.adapters.in_process_agent_client import InProcessAgentClient

# Session (en mémoire — pas de vraie persistance pour l'instant)
from session.infrastructure.adapters.in_memory_session_store import InMemorySessionStore
from session.application.use_cases.create_session import CreateSessionUseCase
from session.application.use_cases.get_session_state import GetSessionStateUseCase
from gateway.infrastructure.adapters.in_process_session_client import InProcessSessionClient

# Gateway : use cases + adapter WebSocket
from gateway.application.use_cases.start_session import StartSessionUseCase
from gateway.application.use_cases.receive_audio_chunk import ReceiveAudioChunkUseCase
from gateway.application.use_cases.request_voice_response import RequestVoiceResponseUseCase
from gateway.application.use_cases.handle_transcription_result import HandleTranscriptionResultUseCase
from gateway.application.use_cases.signal_disconnection import SignalDisconnectionUseCase
from gateway.application.use_cases.request_reconnection import RequestReconnectionUseCase
from gateway.application.use_cases.close_session import CloseSessionUseCase
from gateway.infrastructure.adapters.session_registry import SessionRegistry
from gateway.infrastructure.adapters.websocket_gateway_adapter import WebSocketConnectionHandler
from gateway.infrastructure.adapters.silence_threshold_turn_detector import SilenceThresholdTurnDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway.server")


class ApplicationContainer:
    """Assemble une seule fois toutes les dépendances (modules + use cases)."""

    def __init__(self) -> None:
        # --- ASR ---
        asr_repo = ASRSessionRegistry()
        recognizer = WhisperSpeechRecognizer(
            model_size_partiel="tiny",
            model_size_final="base",
            device="cpu",
            compute_type="int8",
        )
        self.asr_client = InProcessASRClient(
            StartASRSessionUseCase(asr_repo),
            ProcessAudioChunkUseCase(recognizer, asr_repo),
            FinalizeTurnUseCase(recognizer, asr_repo),
            EndASRSessionUseCase(asr_repo),
        )

        # --- TTS ---
        tts_repo = TTSSessionRegistry()
        synthesizer = PiperSpeechSynthesizer(voices_dir=".")
        self.tts_client = InProcessTTSClient(
            StartTTSSessionUseCase(tts_repo),
            SynthesizeTextUseCase(synthesizer, tts_repo),
            EndTTSSessionUseCase(tts_repo),
        )

        # --- Agent ---
        agent_repo = FakeSessionRepositoryAdapter()  # pas de persistance réelle pour l'instant
        agent_registry = AgentSessionRegistry()
        llm = OllamaAdapter(model="llama3.1")
        notifier = FakeScoringNotifierAdapter()  # module scoring pas encore implémenté
        self.agent_client = InProcessAgentClient(
            StartAgentSessionUseCase(agent_repo, agent_registry),
            ConduireEntretienUseCase(llm, agent_repo, notifier, agent_registry),
            EndAgentSessionUseCase(agent_registry),
        )

        # --- Session ---
        session_store = InMemorySessionStore()
        self.session_client = InProcessSessionClient(
            CreateSessionUseCase(session_store),
            GetSessionStateUseCase(session_store),
            session_store,
        )

        # --- Gateway : orchestration + registre des connexions actives ---
        self.gateway_registry = SessionRegistry()
        self.start_session_uc = StartSessionUseCase(
            self.session_client, self.asr_client, self.tts_client, self.agent_client
        )
        self.receive_chunk_uc = ReceiveAudioChunkUseCase(self.asr_client, SilenceThresholdTurnDetector())
        self.request_voice_uc = RequestVoiceResponseUseCase(self.tts_client)
        self.handle_transcription_uc = HandleTranscriptionResultUseCase(
            self.agent_client, self.request_voice_uc
        )
        self.signal_disconnection_uc = SignalDisconnectionUseCase(self.session_client)
        self.request_reconnection_uc = RequestReconnectionUseCase(self.session_client)
        self.close_session_uc = CloseSessionUseCase(
            self.asr_client, self.tts_client, self.agent_client
        )


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
    logger.info("Chargement des modèles (Whisper / Piper / Ollama)...")
    container = ApplicationContainer()

    async def routed_handler(websocket):
        await handler_factory(container, websocket)

    logger.info("Serveur WebSocket démarré sur ws://%s:%s", host, port)
    async with websockets.serve(
        routed_handler, 
        host, 
        port,
        ping_interval=30,  # Envoie un ping toutes les 30s
        ping_timeout=60,   # Tolère jusqu'à 60s d'inactivité/blocage
    ):
        await asyncio.Future()  # tourne indéfiniment


if __name__ == "__main__":
    asyncio.run(main())