from __future__ import annotations

import os
from typing import Dict

from dotenv import load_dotenv
import numpy as np
import sherpa_onnx

from shared.domain import SessionID, TranscriptionResult

load_dotenv()

SAMPLE_RATE = 16_000


class SherpaSpeechRecognizer:

    def __init__(self) -> None:
        tokens = os.environ["TOKENS"]
        encoder = os.environ["ENCODER"]
        decoder = os.environ["DECODER"]
        joiner = os.environ["JOINER"]
        num_threads = int(os.environ["NUM_THREADS"])
        provider = os.environ["PROVIDER"]
        sample_rate = int(os.environ["SAMPLE_RATE"])
        feature_dim = int(os.environ["FEATURE_DIM"])
        decoding_method = os.environ["DECODING_METHOD"]
        enable_endpoint_detection = os.environ["ENABLE_ENDPOINT_DETECTION"].lower() == "true"
        rule1_min_trailing_silence = float(os.environ["RULE1_MIN_TRAILING_SILENCE"])
        rule2_min_trailing_silence = float(os.environ["RULE2_MIN_TRAILING_SILENCE"])
        rule3_min_utterance_length = float(os.environ["RULE3_MIN_UTTERANCE_LENGTH"])

        self._recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=tokens,
            encoder=encoder,
            decoder=decoder,
            joiner=joiner,
            num_threads=num_threads,
            sample_rate=sample_rate,
            feature_dim=feature_dim,
            decoding_method=decoding_method,
            provider=provider,
            enable_endpoint_detection=enable_endpoint_detection,
            rule1_min_trailing_silence=rule1_min_trailing_silence,
            rule2_min_trailing_silence=rule2_min_trailing_silence,
            rule3_min_utterance_length=rule3_min_utterance_length,
        )

        self._streams: Dict[str, sherpa_onnx.OnlineStream] = {}
        self._octets_deja_envoyes: Dict[str, int] = {}

    def _pcm16_to_float32(self, audio_buffer: bytes) -> np.ndarray:
        if not audio_buffer:
            return np.zeros(0, dtype=np.float32)
        audio_int16 = np.frombuffer(audio_buffer, dtype=np.int16)
        return audio_int16.astype(np.float32) / 32768.0

    def _get_or_create_stream(self, session_id: SessionID) -> sherpa_onnx.OnlineStream:
        cle = session_id.value
        stream = self._streams.get(cle)
        if stream is None:
            stream = self._recognizer.create_stream()
            self._streams[cle] = stream
            self._octets_deja_envoyes[cle] = 0
        return stream

    def _pousser_audio_nouveau(self, session_id: SessionID, audio_buffer: bytes) -> sherpa_onnx.OnlineStream:
        stream = self._get_or_create_stream(session_id)
        deja_envoyes = self._octets_deja_envoyes.get(session_id.value, 0)

        nouveaux_octets = audio_buffer[deja_envoyes:]
        if nouveaux_octets:
            samples = self._pcm16_to_float32(nouveaux_octets)
            stream.accept_waveform(SAMPLE_RATE, samples)
            self._octets_deja_envoyes[session_id.value] = len(audio_buffer)

        return stream

    def _decoder_tant_que_pret(self, stream: sherpa_onnx.OnlineStream) -> None:
        while self._recognizer.is_ready(stream):
            self._recognizer.decode_stream(stream)

    async def transcrire_partiel(self, session_id: SessionID, audio_buffer: bytes, language: str) -> TranscriptionResult:
        return await self._to_thread(self._transcrire_partiel_sync, session_id, audio_buffer, language)

    async def transcrire_final(self, session_id: SessionID, audio_buffer: bytes, language: str) -> TranscriptionResult:
        return await self._to_thread(self._transcrire_final_sync, session_id, audio_buffer, language)

    async def _to_thread(self, fonction, *args):
        import asyncio
        return await asyncio.to_thread(fonction, *args)

    def _transcrire_partiel_sync(self, session_id: SessionID, audio_buffer: bytes, language: str) -> TranscriptionResult:
        stream = self._pousser_audio_nouveau(session_id, audio_buffer)
        self._decoder_tant_que_pret(stream)

        texte = self._recognizer.get_result(stream).strip()
        return TranscriptionResult(session_id=session_id, is_final=False, text=texte, confidence=1.0)

    def _transcrire_final_sync(self, session_id: SessionID, audio_buffer: bytes, language: str) -> TranscriptionResult:
        stream = self._pousser_audio_nouveau(session_id, audio_buffer)

        # signale la fin de l'énoncé pour vider le flux (tail padding)
        stream.input_finished()
        self._decoder_tant_que_pret(stream)

        texte = self._recognizer.get_result(stream).strip()
        resultat = TranscriptionResult(session_id=session_id, is_final=True, text=texte, confidence=1.0)

        self._reinitialiser_flux(session_id)
        return resultat

    def _reinitialiser_flux(self, session_id: SessionID) -> None:
        cle = session_id.value
        self._streams.pop(cle, None)
        self._octets_deja_envoyes.pop(cle, None)

    def est_fin_de_parole_detectee(self, session_id: SessionID) -> bool:

        cle = session_id.value
        stream = self._streams.get(cle)
        if stream is None:
            return False
        return self._recognizer.is_endpoint(stream)

    def fermer_session(self, session_id: SessionID) -> None:
        self._reinitialiser_flux(session_id)