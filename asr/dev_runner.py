"""
Vérifie que le module ASR fonctionne seul, sans le gateway ni modèle
réel. Lance : python -m  dev_runner
"""
import asyncio

from  domain.value_objects.session_id import SessionId
from  domain.value_objects.audio_chunk import AudioChunk
from  application.use_cases.start_session import StartASRSessionUseCase
from  application.use_cases.process_audio_chunk import ProcessAudioChunkUseCase
from  application.use_cases.finalize_turn import FinalizeTurnUseCase
from  infrastructure.adapters.fake_speech_recognizer import FakeSpeechRecognizer


async def main() -> None:
    recognizer = FakeSpeechRecognizer()
    start = StartASRSessionUseCase()
    process_chunk = ProcessAudioChunkUseCase(recognizer)
    finalize = FinalizeTurnUseCase(recognizer)

    session = start.executer(SessionId("demo-asr-001"), language="fr")

    for i in range(3):
        chunk = AudioChunk(data=b"\x00" * 320, sequence_number=i + 1)
        resultat = await process_chunk.executer(session, chunk)
        print(f"[partiel #{i+1}] {resultat.text} (confiance={resultat.confidence})")

    resultat_final = await finalize.executer(session)
    print(f"[final] {resultat_final.text} (confiance={resultat_final.confidence})")


if __name__ == "__main__":
    asyncio.run(main())