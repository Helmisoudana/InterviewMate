"""Teste avec le vrai moteur Piper. Lance : python -m tts.dev_runner (depuis la racine)"""
import asyncio
import wave

from tts.composition_root import TTSContainer
from shared.domain import SessionID as TTSSessionId


async def main() -> None:
    container = TTSContainer(voices_dir=".")
    session_id = TTSSessionId("test-piper-001")

    container.start_session.executer(session_id, voice="fr_FR-siwis-medium")

    tous_les_octets = bytearray()
    async for chunk in container.synthesize_text.executer(session_id, "Bonjour, pouvez-vous vous présenter ?"):
        tous_les_octets.extend(chunk.data)

    with wave.open("sortie_test.wav", "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(bytes(tous_les_octets))

    print(f"Généré : sortie_test.wav ({len(tous_les_octets)} octets)")
    container.end_session.executer(session_id)


if __name__ == "__main__":
    asyncio.run(main())