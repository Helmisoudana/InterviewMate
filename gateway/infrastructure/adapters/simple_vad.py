
import array


def is_silence(pcm16_bytes: bytes, threshold: int = 500) -> bool:
    if not pcm16_bytes:
        return True
    samples = array.array("h")
    try:
        samples.frombytes(pcm16_bytes)
    except ValueError:
        return True
    if not samples:
        return True
    rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
    return rms < threshold