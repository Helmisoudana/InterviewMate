import asyncio

from shared.domain import SessionID, AudioChunk

# ASR imports
from asr.infrastructure.adapters.session_registry import ASRSessionRegistry
from asr.infrastructure.adapters.fake_speech_recognizer import FakeSpeechRecognizer
from asr.application.use_cases.start_session import StartASRSessionUseCase
from asr.application.use_cases.process_audio_chunk import ProcessAudioChunkUseCase
from asr.application.use_cases.finalize_turn import FinalizeTurnUseCase
from asr.application.use_cases.end_session import EndASRSessionUseCase
from gateway.infrastructure.adapters.in_process_asr_client import InProcessASRClient

# TTS imports
from tts.infrastructure.adapters.session_registry import TTSSessionRegistry
from tts.infrastructure.adapters.fake_speech_synthesizer import FakeSpeechSynthesizer
from tts.application.use_cases.start_session import StartTTSSessionUseCase
from tts.application.use_cases.synthesize_text import SynthesizeTextUseCase
from tts.application.use_cases.end_session import EndTTSSessionUseCase
from gateway.infrastructure.adapters.in_process_tts_client import InProcessTTSClient

# Agent imports
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry
from agent.application.use_cases.start_session import StartAgentSessionUseCase
from agent.application.use_cases.conduire_entretien import ConduireEntretienUseCase
from agent.application.use_cases.end_session import EndAgentSessionUseCase
from tests.test_agent import FakeSessionRepo, FakeLLM, FakeScoringNotifier
from gateway.infrastructure.adapters.in_process_agent_client import InProcessAgentClient

# Session imports
from session.infrastructure.adapters.in_memory_session_store import InMemorySessionStore
from session.application.use_cases.create_session import CreateSessionUseCase
from session.application.use_cases.get_session_state import GetSessionStateUseCase
from gateway.infrastructure.adapters.in_process_session_client import InProcessSessionClient

# Gateway Orchestration Use Cases
from gateway.application.use_cases.start_session import StartSessionUseCase
from gateway.domain.entities.entities import GatewaySession
from gateway.application.use_cases.request_voice_response import RequestVoiceResponseUseCase


class ConsoleBroadcaster:
    async def envoyer_audio_candidat(self, session_id: SessionID, chunk: AudioChunk) -> None:
        print(f"[Broadcaster] Envoi audio candidat pour {session_id.value} : {len(chunk.data)} octets (final={chunk.is_final})")


async def main():
    session_id = SessionID("demo-orchestration-001")

    # 1. Wire ASR
    asr_repo = ASRSessionRegistry()
    fake_recognizer = FakeSpeechRecognizer()
    asr_start = StartASRSessionUseCase(asr_repo)
    asr_process = ProcessAudioChunkUseCase(fake_recognizer, asr_repo)
    asr_finalize = FinalizeTurnUseCase(fake_recognizer, asr_repo)
    asr_end = EndASRSessionUseCase(asr_repo)
    asr_client = InProcessASRClient(asr_start, asr_process, asr_finalize, asr_end)

    # 2. Wire TTS
    tts_repo = TTSSessionRegistry()
    fake_synthesizer = FakeSpeechSynthesizer()
    tts_start = StartTTSSessionUseCase(tts_repo)
    tts_synthesize = SynthesizeTextUseCase(fake_synthesizer, tts_repo)
    tts_end = EndTTSSessionUseCase(tts_repo)
    tts_client = InProcessTTSClient(tts_start, tts_synthesize, tts_end)

    # 3. Wire Agent
    agent_repo = FakeSessionRepo()
    agent_registry = AgentSessionRegistry()
    fake_llm = FakeLLM([{"qualite": "correcte", "comportement_inapproprie": False, "question": "Bonjour ! Parlez-moi de votre expérience avec Python."}])
    fake_notifier = FakeScoringNotifier()
    agent_start = StartAgentSessionUseCase(agent_repo, agent_registry)
    agent_conduire = ConduireEntretienUseCase(fake_llm, agent_repo, fake_notifier, agent_registry)
    agent_end = EndAgentSessionUseCase(agent_registry)
    agent_client = InProcessAgentClient(agent_start, agent_conduire, agent_end)

    # 4. Wire Session
    session_store = InMemorySessionStore()
    session_create = CreateSessionUseCase(session_store)
    session_get = GetSessionStateUseCase(session_store)
    session_client = InProcessSessionClient(session_create, session_get, session_store)

    # 5. Wire Gateway orchestrator
    gateway_session = GatewaySession(session_id)
    start_session_uc = StartSessionUseCase(session_client, asr_client, tts_client, agent_client)
    request_voice_uc = RequestVoiceResponseUseCase(agent_client, tts_client)

    # Start Session
    print("--- Initialisation de la session ---")
    await start_session_uc.executer(gateway_session)

    # Handle transcription result & generate response
    print("\n--- Simulation de la réponse candidat ---")
    broadcaster = ConsoleBroadcaster()
    await request_voice_uc.executer(gateway_session, "Bonjour, j'ai 5 ans d'expérience.", broadcaster)

    print("\nOrchestration terminée avec succès !")


if __name__ == "__main__":
    asyncio.run(main())