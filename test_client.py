import asyncio
import json
import websockets

# Modifier le port si gateway/server.py utilise un autre port (ex: 8000, 8765, etc.)
SERVER_URI = "ws://localhost:8765"

async def test_websocket_flow():
    print(f"🔌 Connexion à {SERVER_URI}...")
    
    async with websockets.connect(SERVER_URI) as ws:
        print("✅ Connecté au serveur WebSocket !")

        # 1. Envoi du message d'initialisation
        payload_start = {
            "type": "start_session",
            "session_id": "session-test-integration-123"
        }
        await ws.send(json.dumps(payload_start))
        print("📤 Message 'start_session' envoyé.")

        await asyncio.sleep(2)

        # 2. Envoi du message de clôture (déclenche le module Scoring)
        payload_close = {
            "type": "close_session",
            "session_id": "session-test-integration-123"
        }
        await ws.send(json.dumps(payload_close))
        print("📤 Message 'close_session' envoyé. Attente du retour du serveur...")

        # 3. Réception des messages de réponse
        try:
            while True:
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                print(f"📥 Message reçu : {response}")
        except asyncio.TimeoutError:
            print("\n⏰ Fin d'écoute (Timeout atteint).")

if __name__ == "__main__":
    asyncio.run(test_websocket_flow())