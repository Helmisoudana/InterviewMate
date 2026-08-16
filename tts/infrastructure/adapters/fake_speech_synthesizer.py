import asyncio
from typing import AsyncIterator


class FakeSpeechSynthesizer:
    async def synthetiser(self, texte: str, voice: str) -> AsyncIterator[bytes]:
        for _ in range(3):
            await asyncio.sleep(0.02)
            yield b"\x00" * 640