import array
import logging
import os

logger = logging.getLogger(__name__)


DEFAULT_THRESHOLD = int(os.environ.get("VAD_RMS_THRESHOLD", "500"))


def calculer_rms(pcm16_bytes: bytes) -> float:

    if not pcm16_bytes:
        return 0.0
    samples = array.array("h")
    try:
        samples.frombytes(pcm16_bytes)
    except ValueError:
        return 0.0
    if not samples:
        return 0.0
    return (sum(s * s for s in samples) / len(samples)) ** 0.5


def is_silence(pcm16_bytes: bytes, threshold: int = DEFAULT_THRESHOLD) -> bool:
    if not pcm16_bytes:
        return True
    return calculer_rms(pcm16_bytes) < threshold