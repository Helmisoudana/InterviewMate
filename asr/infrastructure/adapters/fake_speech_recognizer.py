
import asyncio

from  domain.value_objects.transcription_result import TranscriptionResult


class FakeSpeechRecognizer:
    async def transcrire_partiel(self, audio_buffer: bytes, language: str) -> TranscriptionResult:
        await asyncio.sleep(0)
        return TranscriptionResult(type="partial", text="je pense que", confidence=0.6)

    async def transcrire_final(self, audio_buffer: bytes, language: str) -> TranscriptionResult:
        await asyncio.sleep(0)
        return TranscriptionResult(
            type="final",
            text="je pense que le pattern singleton est utile ici",
            confidence=0.91,
        )