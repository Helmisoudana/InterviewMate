

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# ---- ASR ------------------------------------------------------------
from asr.infrastructure.adapters.whisper_speech_recognizer import WhisperSpeechRecognizer
from asr.infrastructure.adapters.session_registry import ASRSessionRegistry
from asr.infrastructure.adapters.gateway_engine_adapter import ASRGatewayEngineAdapter

# ---- TTS --------------------------------------------------------------
from tts.infrastructure.adapters.piper_speech_synthesizer import PiperSpeechSynthesizer
from tts.infrastructure.adapters.session_registry import TTSSessionRegistry
from tts.infrastructure.adapters.gateway_engine_adapter import TTSGatewayEngineAdapter

# ---- Agent (câblé ici avec ses propres fakes tant que son responsable
# n'a pas fourni de vraie persistance / notifier de scoring) -----------
from agent.infrastructure.adapters.ollama_adapter import OllamaAdapter
from agent.infrastructure.fakes.fake_session_repository_adapter import FakeSessionRepositoryAdapter
from agent.infrastructure.fakes.fake_scoring_notifier_adapter import FakeScoringNotifierAdapter
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry
from agent.infrastructure.adapters.gateway_engine_adapter import AgentGatewayEngineAdapter

# ---- Session ------------------------------------------------------
from session.infrastructure.adapters.in_memory_session_store import InMemorySessionStore
from session.application.use_cases.create_session import CreateSessionUseCase
from session.application.use_cases.get_session_state import GetSessionStateUseCase
from session.infrastructure.adapters.gateway_engine_adapter import SessionGatewayEngineAdapter

# ---- Gateway : clients in-process (enveloppent les engines ci-dessus) -
from gateway.infrastructure.adapters.in_process_asr_client import InProcessASRClient
from gateway.infrastructure.adapters.in_process_tts_client import InProcessTTSClient
from gateway.infrastructure.adapters.in_process_agent_client import InProcessAgentClient
from gateway.infrastructure.adapters.in_process_session_client import InProcessSessionClient

# ---- Gateway : reste de l'infrastructure -------------------------------
from gateway.infrastructure.adapters.session_registry import SessionRegistry
from gateway.infrastructure.adapters.silence_threshold_turn_detector import SilenceThresholdTurnDetector

# ---- Gateway : use cases -----------------------------------------------
from gateway.application.use_cases.start_session import StartSessionUseCase
from gateway.application.use_cases.receive_audio_chunk import ReceiveAudioChunkUseCase
from gateway.application.use_cases.request_voice_response import RequestVoiceResponseUseCase
from gateway.application.use_cases.handle_transcription_result import HandleTranscriptionResultUseCase
from gateway.application.use_cases.signal_disconnection import SignalDisconnectionUseCase
from gateway.application.use_cases.request_reconnection import RequestReconnectionUseCase
from gateway.application.use_cases.close_session import CloseSessionUseCase


@dataclass
class Container:
    """Regroupe uniquement ce dont main.py a besoin pour servir une
    connexion WebSocket : le registre partagé (pour les reconnexions)
    et les use cases, tous réutilisables entre connexions."""

    gateway_registry: SessionRegistry
    asr_client: InProcessASRClient
    start_session: StartSessionUseCase
    receive_chunk: ReceiveAudioChunkUseCase
    request_voice: RequestVoiceResponseUseCase
    handle_transcription: HandleTranscriptionResultUseCase
    signal_disconnection: SignalDisconnectionUseCase
    request_reconnection: RequestReconnectionUseCase
    close_session: CloseSessionUseCase


def build_container() -> Container:
    # ---- 1. Moteurs réels, configurés via .env ---------------------------
    whisper = WhisperSpeechRecognizer(
        model_size_partiel=os.getenv("WHISPER_MODEL_PARTIEL", "tiny"),
        model_size_final=os.getenv("WHISPER_MODEL_FINAL", "base"),
        device=os.getenv("WHISPER_DEVICE", "cpu"),
        compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
    )
    piper = PiperSpeechSynthesizer(voices_dir=os.getenv("PIPER_VOICES_DIR", "./voices"))
    ollama = OllamaAdapter(model=os.getenv("OLLAMA_MODEL", "llama3"))

    # ---- 2. Store du module session -------------------------------------
    session_store = InMemorySessionStore()

    # ---- 3. Engine adapters (un par module cible) -----------------------
    asr_engine = ASRGatewayEngineAdapter(ASRSessionRegistry(), whisper)
    tts_engine = TTSGatewayEngineAdapter(TTSSessionRegistry(), piper)
    agent_engine = AgentGatewayEngineAdapter(
        AgentSessionRegistry(),
        ollama,
        FakeSessionRepositoryAdapter(),   # à remplacer par une vraie persistance côté agent
        FakeScoringNotifierAdapter(),     # idem pour le scoring
    )
    session_engine = SessionGatewayEngineAdapter(
        session_store,
        CreateSessionUseCase(),
        GetSessionStateUseCase(session_store),
    )

    # ---- 4. Clients in-process côté gateway ------------------------------
    asr_client = InProcessASRClient(asr_engine)
    tts_client = InProcessTTSClient(tts_engine)
    agent_client = InProcessAgentClient(agent_engine)
    session_client = InProcessSessionClient(session_engine)

    # ---- 5. Reste de l'infra gateway, configuré via .env -----------------
    gateway_registry = SessionRegistry()
    turn_detector = SilenceThresholdTurnDetector(
        seuil_silence_ms=int(os.getenv("SEUIL_SILENCE_MS", "1000"))
    )

    # ---- 6. Use cases (partagés entre toutes les connexions) -------------
    start_session = StartSessionUseCase(
        session_client,
        asr_client,
        tts_client,
        agent_client,
        default_voice=os.getenv("DEFAULT_VOICE", "fr_FR-siwis-medium"),
    )
    receive_chunk = ReceiveAudioChunkUseCase(asr_client, turn_detector)
    request_voice = RequestVoiceResponseUseCase(tts_client)
    handle_transcription = HandleTranscriptionResultUseCase(agent_client, request_voice)
    signal_disconnection = SignalDisconnectionUseCase(session_client)
    request_reconnection = RequestReconnectionUseCase(session_client)
    close_session = CloseSessionUseCase(asr_client, tts_client, agent_client)

    return Container(
        gateway_registry=gateway_registry,
        asr_client=asr_client,
        start_session=start_session,
        receive_chunk=receive_chunk,
        request_voice=request_voice,
        handle_transcription=handle_transcription,
        signal_disconnection=signal_disconnection,
        request_reconnection=request_reconnection,
        close_session=close_session,
    )