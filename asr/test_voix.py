import os
import warnings
import asyncio
import numpy as np
import sounddevice as sd

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")

from asr.infrastructure.adapters.whisper_speech_recognizer import WhisperSpeechRecognizer

SAMPLE_RATE = 16000
DURATION = 10 

async def main():
    print("⏳ Chargement unique du modèle en mémoire GPU...")
    recognizer = WhisperSpeechRecognizer(
        model_size_partiel="medium",
        model_size_final="medium",
        device="cuda",
        compute_type="float16"
    )
    print("✅ Modèle chargé et prêt !")

    # Boucle de test : le modèle reste en mémoire VRAM
    while True:
        entree = input("\n👉 Appuyez sur [Entrée] pour enregistrer (ou 'q' pour quitter) : ")
        if entree.lower() == 'q':
            break

        print(f"🎙️ Enregistrement ({DURATION}s)... Parlez !")
        audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
        sd.wait()
        print("✅ Enregistrement terminé.")

        print("📝 Transcription...")
        resultat = await recognizer.transcrire_final("session-1", audio_data.tobytes(), "fr")

        print("\n" + "="*50)
        print(f"🗣️  Texte : {resultat.text}")
        print(f"🎯 Confiance : {resultat.confidence:.2%}")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(main())