"""
Charge un fichier .wav deja existant, le reechantillonne automatiquement
en 16kHz si besoin, et le passe a WhisperSpeechRecognizer (sur GPU/CUDA)
pour voir le texte transcrit. Aucun enregistrement live, aucun micro.

Installation prealable (si pas deja installe) :
    pip install scipy nvidia-cublas-cu12 nvidia-cudnn-cu12

Lancement :
    python test_whisper_depuis_wav.py mon_fichier.wav
"""
import sys
import asyncio
import wave
import os
import glob
import numpy as np
from scipy.signal import resample_poly
from math import gcd

# Windows ne cherche pas les DLL dans site-packages par defaut.
# On ajoute explicitement les dossiers des paquets nvidia-*-cu12 installes via pip.
if sys.platform == "win32":
    for motif in ("nvidia/cublas/bin", "nvidia/cudnn/bin", "nvidia/cuda_nvrtc/bin"):
        for dossier in glob.glob(os.path.join(os.path.dirname(sys.executable), "..", "Lib", "site-packages", motif)):
            os.add_dll_directory(os.path.abspath(dossier))

from asr.infrastructure.adapters.whisper_speech_recognizer import WhisperSpeechRecognizer
from shared.domain import SessionID

TAUX_CIBLE = 16_000


def reechantillonner(samples: np.ndarray, taux_source: int, taux_cible: int) -> np.ndarray:
    if taux_source == taux_cible:
        return samples
    pgcd = gcd(taux_source, taux_cible)
    up = taux_cible // pgcd
    down = taux_source // pgcd
    resample_float = resample_poly(samples.astype(np.float64), up, down)
    resample_int16 = np.clip(resample_float, -32768, 32767).astype(np.int16)
    return resample_int16


def charger_wav_en_pcm16(chemin_fichier: str) -> bytes:
    with wave.open(chemin_fichier, "rb") as f:
        n_canaux = f.getnchannels()
        largeur_echantillon = f.getsampwidth()
        taux = f.getframerate()
        n_frames = f.getnframes()
        raw = f.readframes(n_frames)

    print(f"Fichier : {chemin_fichier}")
    print(f"  canaux={n_canaux}, largeur_echantillon={largeur_echantillon} octets, taux={taux} Hz, duree={n_frames / taux:.2f}s")

    if largeur_echantillon != 2:
        raise ValueError(f"Le fichier n'est pas en 16 bits (int16), largeur={largeur_echantillon} octets. Reconvertis-le d'abord.")

    samples = np.frombuffer(raw, dtype=np.int16)

    if n_canaux == 2:
        print("  Fichier stereo detecte -> conversion en mono (moyenne des 2 canaux)")
        samples = samples.reshape(-1, 2).mean(axis=1).astype(np.int16)
    elif n_canaux != 1:
        raise ValueError(f"Le fichier a {n_canaux} canaux, seul mono (1) ou stereo (2) sont geres ici.")

    if taux != TAUX_CIBLE:
        print(f"  Reechantillonnage {taux} Hz -> {TAUX_CIBLE} Hz...")
        samples = reechantillonner(samples, taux, TAUX_CIBLE)
        print(f"  Reechantillonnage termine, nouvelle duree = {len(samples) / TAUX_CIBLE:.2f}s")

    rms = np.sqrt(np.mean(samples.astype(np.float64) ** 2)) if len(samples) else 0.0
    print(f"  RMS du signal (apres traitement) : {rms:.1f} (silence typique < 500, voix normale > 1000-3000)")

    return samples.tobytes()


async def main(chemin_fichier: str):
    audio_bytes = charger_wav_en_pcm16(chemin_fichier)

    print("Chargement du modele Whisper (GPU/CUDA)... patiente...")
    recognizer = WhisperSpeechRecognizer(device="cuda", compute_type="float16")
    print("Modele charge avec succes.")
    session_id = SessionID("test-depuis-wav")

    print("Lancement de la transcription...")
    resultat = await recognizer.transcrire_final(session_id, audio_bytes, language="fr")

    print("\n=== RESULTAT DE LA TRANSCRIPTION ===")
    print(f"Texte       : {resultat.text!r}")
    print(f"Confiance   : {resultat.confidence:.3f}")
    print(f"Is final    : {resultat.is_final}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python test_whisper_depuis_wav.py chemin_vers_fichier.wav")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))