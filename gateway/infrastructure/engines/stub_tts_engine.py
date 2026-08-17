import asyncio
from typing import AsyncIterator

from  domain.value_objects.session_id import SessionId


class StubTTSEngine:
    """Moteur factice : renvoie de faux chunks audio en streaming."""

    async def synthetiser(self, session_id: SessionId, texte: str) -> AsyncIterator[bytes]:
        for _ in range(3):
            await asyncio.sleep(0.05)
            yield b"\x00" * 320  # faux chunk audio