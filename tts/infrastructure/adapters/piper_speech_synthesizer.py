
from __future__ import annotations

import asyncio
from typing import AsyncIterator, Dict

import numpy as np
from piper import PiperVoice

SAMPLE_RATE_CIBLE = 16_000


class PiperSpeechSynthesizer:
    def __init__(self, voices_dir: str = ".") -> None:
        self._voices_dir = voices_dir
        self._voix_chargees: Dict[str, PiperVoice] = {}

    def _obtenir_voix(self, voice: str) -> PiperVoice:
        if voice not in self._voix_chargees:
            chemin_modele = f"{self._voices_dir}/{voice}.onnx"
            self._voix_chargees[voice] = PiperVoice.load(chemin_modele)
        return self._voix_chargees[voice]

    async def synthetiser(self, texte: str, voice: str) -> AsyncIterator[bytes]:
        piper_voice = self._obtenir_voix(voice)
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def produire() -> None:
            try:
                for chunk in piper_voice.synthesize(texte):
                    audio_16k = self._resampler(chunk.audio_int16_bytes, piper_voice.config.sample_rate)
                    loop.call_soon_threadsafe(queue.put_nowait, audio_16k)
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)  # signal de fin

        loop.run_in_executor(None, produire)

        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

    def _resampler(self, audio_bytes: bytes, sample_rate_source: int) -> bytes:
        if sample_rate_source == SAMPLE_RATE_CIBLE:
            return audio_bytes

        audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
        duree = len(audio) / sample_rate_source
        n_cible = int(duree * SAMPLE_RATE_CIBLE)

        x_source = np.linspace(0, duree, num=len(audio), endpoint=False)
        x_cible = np.linspace(0, duree, num=n_cible, endpoint=False)
        audio_reechantillonne = np.interp(x_cible, x_source, audio)

        return audio_reechantillonne.astype(np.int16).tobytes()