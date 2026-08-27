import asyncio
import sys
import numpy as np
import sounddevice as sd

from shared.domain import SessionID, AudioChunk
from asr.application.use_cases.start_session import StartASRSessionUseCase
from asr.application.use_cases.process_audio_chunk import ProcessAudioChunkUseCase
from asr.application.use_cases.finalize_turn import FinalizeTurnUseCase
from asr.infrastructure.adapters.sherpa_speech_recognizer import SherpaSpeechRecognizer
from asr.infrastructure.adapters.session_registry import ASRSessionRegistry

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE_SAMPLES = 1600


async def capturer_et_transcrire():
    # -------------------------------------------------------------------------
    # Initialisation sans arguments directes s'ils sont gérés en interne par l'adaptateur
    # (Ou avec l'objet de config / variables requises par votre implémentation)
    # -------------------------------------------------------------------------
    try:
        recognizer = SherpaSpeechRecognizer(
            tokens_path="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/tokens.txt",
            encoder_path="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/encoder-epoch-29-avg-9-with-averaged-model.int8.onnx",
            decoder_path="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/decoder-epoch-29-avg-9-with-averaged-model.onnx",
            joiner_path="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/joiner-epoch-29-avg-9-with-averaged-model.int8.onnx",
            num_threads=2,
            provider="cpu",
        )
    except TypeError:
        # Si votre classe SherpaSpeechRecognizer ne prend aucun paramètre et lit le tout depuis os.getenv() ou une config
        recognizer = SherpaSpeechRecognizer()

    repo = ASRSessionRegistry()
    start = StartASRSessionUseCase(repo)
    process_chunk = ProcessAudioChunkUseCase(recognizer, repo)
    finalize = FinalizeTurnUseCase(recognizer, repo)

    session_id = SessionID("test-mic-direct")
    start.executer(session_id, language="fr")

    loop = asyncio.get_running_loop()
    audio_queue = asyncio.Queue()
    sequence_number = 0

    def callback_audio(indata, frames, time_info, status):
        if status:
            print(f"[Warning] Status Audio: {status}", file=sys.stderr)
        pcm16_data = (indata * 32767).astype(np.int16).tobytes()
        loop.call_soon_threadsafe(audio_queue.put_nowait, pcm16_data)

    print("\n" + "=" * 50)
    print("🎙️ MICROPHONE ACTIF - Parlez dans votre micro...")
    print("Appuyez sur Ctrl+C pour arrêter le test.")
    print("=" * 50 + "\n")

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='float32',
        blocksize=CHUNK_SIZE_SAMPLES,
        callback=callback_audio
    )

    try:
        with stream:
            while True:
                data = await audio_queue.get()
                sequence_number += 1
                chunk = AudioChunk(session_id=session_id, data=data, sequence_number=sequence_number)
                
                resultat = await process_chunk.executer(session_id, chunk)
                if resultat and resultat.text:
                    print(f"\r[partiel] {resultat.text} (confiance={resultat.confidence:.2f})", end="", flush=True)

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt de la capture micro...")
    finally:
        resultat_final = await finalize.executer(session_id)
        if resultat_final:
            print(f"\n[FINAL] {resultat_final.text} (confiance={resultat_final.confidence:.2f})\n")


if __name__ == "__main__":
    try:
        asyncio.run(capturer_et_transcrire())
    except KeyboardInterrupt:
        pass