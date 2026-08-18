

import asyncio
import logging
import os

import websockets
from dotenv import load_dotenv

from container import build_container
from gateway.infrastructure.adapters.websocket_gateway_adapter import WebSocketConnectionHandler

load_dotenv()

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8765"))

    container = build_container()

    async def handler(websocket) -> None:
        connexion = WebSocketConnectionHandler(
            websocket,
            container.gateway_registry,
            container.asr_client,
            container.start_session,
            container.receive_chunk,
            container.request_voice,
            container.signal_disconnection,
            container.request_reconnection,
            container.close_session,
            container.handle_transcription,
        )
        await connexion.gerer_connexion()

    async with websockets.serve(handler, host, port):
        logging.info("ERPilot voice gateway démarré sur ws://%s:%s", host, port)
        await asyncio.Future()  # tourne indéfiniment


if __name__ == "__main__":
    asyncio.run(main())