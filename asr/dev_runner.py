"""
Teste WhisperSpeechRecognizer avec un vrai fichier .wav.
Usage : python -m  dev_runner_real_audio chemin/vers/fichier.wav

Le fichier doit être en PCM 16 bits mono 16 kHz. Pour convertir un
fichier quelconque avec ffmpeg :
  ffmpeg -i entree.mp3 -ar 16000 -ac 1 -c:a pcm_s16le sortie.wav
"""
import asyncio
import sys
import wave

from shared.domain import SessionID
from shared.domain import AudioChunk
from asr.application.use_cases.start_session import StartASRSessionUseCase
from asr.application.use_cases.process_audio_chunk import ProcessAudioChunkUseCase
from asr.application.use_cases.finalize_turn import FinalizeTurnUseCase
from asr.infrastructure.adapters.sherpa_speech_recognizer import SherpaSpeechRecognizer
from asr.infrastructure.adapters.session_registry import ASRSessionRegistry


def lire_wav_en_chunks(chemin: str, taille_chunk_octets: int = 3200):
    with wave.open(chemin, "rb") as wav:
        assert wav.getframerate() == 16000, "Le fichier doit être en 16kHz"
        assert wav.getnchannels() == 1, "Le fichier doit être mono"
        assert wav.getsampwidth() == 2, "Le fichier doit être en 16 bits"
        data = wav.readframes(wav.getnframes())
    for i in range(0, len(data), taille_chunk_octets):
        yield data[i:i + taille_chunk_octets]


async def main(chemin_wav: str) -> None:
    recognizer = SherpaSpeechRecognizer(
        tokens="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/tokens.txt",
        encoder="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/encoder-epoch-29-avg-9-with-averaged-model.int8.onnx",
        decoder="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/decoder-epoch-29-avg-9-with-averaged-model.onnx",
        joiner="models/sherpa/sherpa-onnx-streaming-zipformer-fr-2023-04-14/joiner-epoch-29-avg-9-with-averaged-model.int8.onnx",
        num_threads=2,
        provider="cpu",
    )
    repo = ASRSessionRegistry()
    start = StartASRSessionUseCase(repo)
    process_chunk = ProcessAudioChunkUseCase(recognizer, repo)
    finalize = FinalizeTurnUseCase(recognizer, repo)

    session_id = SessionID("test-audio-reel")
    start.executer(session_id, language="fr")

    for i, morceau in enumerate(lire_wav_en_chunks(chemin_wav)):
        chunk = AudioChunk(session_id=session_id, data=morceau, sequence_number=i + 1)
        resultat = await process_chunk.executer(session_id, chunk)
        if resultat.text:
            print(f"[partiel] {resultat.text} (confiance={resultat.confidence:.2f})")

    resultat_final = await finalize.executer(session_id)
    print(f"\n[FINAL] {resultat_final.text} (confiance={resultat_final.confidence:.2f})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python -m  dev_runner_real_audio chemin/vers/fichier.wav")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))