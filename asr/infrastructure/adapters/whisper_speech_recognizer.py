
from __future__ import annotations

import asyncio
import numpy as np
from faster_whisper import WhisperModel

from domain.value_objects.transcription_result import TranscriptionResult

SAMPLE_RATE = 16_000
OCTETS_PAR_ECHANTILLON = 2  
DUREE_MIN_SECONDES = 0.3


class WhisperSpeechRecognizer:
    def __init__(
        self,
        model_size_partiel: str = "tiny",
        model_size_final: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        fenetre_max_secondes: float = 5.0,
    ) -> None:
        
        self._model_partiel = WhisperModel(model_size_partiel, device=device, compute_type=compute_type)
        self._model_final = WhisperModel(model_size_final, device=device, compute_type=compute_type)
        self._fenetre_max_secondes = fenetre_max_secondes


    def _pcm16_to_float32(self, audio_buffer: bytes) -> np.ndarray:
        if not audio_buffer:
            return np.zeros(0, dtype=np.float32)
        audio_int16 = np.frombuffer(audio_buffer, dtype=np.int16)
        return audio_int16.astype(np.float32) / 32768.0

    def _duree_secondes(self, audio: np.ndarray) -> float:
        return len(audio) / SAMPLE_RATE

    def _tronquer_a_la_fenetre(self, audio: np.ndarray) -> np.ndarray:
        taille_max = int(self._fenetre_max_secondes * SAMPLE_RATE)
        if len(audio) <= taille_max:
            return audio
        return audio[-taille_max:]


    async def transcrire_partiel(self, audio_buffer: bytes, language: str) -> TranscriptionResult:
        return await asyncio.to_thread(self._transcrire_partiel_sync, audio_buffer, language)

    async def transcrire_final(self, audio_buffer: bytes, language: str) -> TranscriptionResult:
        return await asyncio.to_thread(self._transcrire_final_sync, audio_buffer, language)


    def _transcrire_partiel_sync(self, audio_buffer: bytes, language: str) -> TranscriptionResult:
        audio = self._pcm16_to_float32(audio_buffer)
        audio = self._tronquer_a_la_fenetre(audio)

        if self._duree_secondes(audio) < DUREE_MIN_SECONDES:
            return TranscriptionResult(type="partial", text="", confidence=0.0)

        segments, _info = self._model_partiel.transcribe(
            audio,
            language=language,
            beam_size=1,       
            vad_filter=True,
        )
        return self._construire_resultat(segments, "partial")

    def _transcrire_final_sync(self, audio_buffer: bytes, language: str) -> TranscriptionResult:
        audio = self._pcm16_to_float32(audio_buffer)
        
        if self._duree_secondes(audio) < DUREE_MIN_SECONDES:
            return TranscriptionResult(type="final", text="", confidence=0.0)

        segments, _info = self._model_final.transcribe(
            audio,
            language=language,
            beam_size=5,
            vad_filter=True,
        )
        return self._construire_resultat(segments, "final")

    def _construire_resultat(self, segments, type_: str) -> TranscriptionResult:
        segments = list(segments) 
        if not segments:
            return TranscriptionResult(type=type_, text="", confidence=0.0)

        texte = " ".join(seg.text.strip() for seg in segments).strip()
        confiance = self._confiance_moyenne(segments)
        return TranscriptionResult(type=type_, text=texte, confidence=confiance)

    def _confiance_moyenne(self, segments) -> float:
        scores = []
        for seg in segments:
            score = np.exp(seg.avg_logprob) * (1 - seg.no_speech_prob)
            scores.append(score)
        confiance = float(np.mean(scores)) if scores else 0.0
        return max(0.0, min(1.0, confiance))