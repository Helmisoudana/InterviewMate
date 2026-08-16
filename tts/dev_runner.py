"""Teste avec le vrai moteur Piper. Lance : python -m tts.dev_runner_real (depuis la racine)"""
import asyncio
import wave

from composition_root import construire_tts_engine
from domain.value_objects.session_id import SessionId as TTSSessionId


class FauxSessionId:
    def __init__(self, value):
        self.value = value


async def main() -> None:
    engine = construire_tts_engine(voices_dir=".")
    session_id = FauxSessionId("test-piper-001")

    await engine.demarrer_session(session_id, voice="fr_FR-siwis-medium")

    tous_les_octets = bytearray()
    async for chunk in engine.synthetiser(session_id, "Bonjour, pouvez-vous vous présenter ?"):
        tous_les_octets.extend(chunk)

    with wave.open("sortie_test.wav", "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(bytes(tous_les_octets))

    print(f"Généré : sortie_test.wav ({len(tous_les_octets)} octets)")
    await engine.terminer_session(session_id)


if __name__ == "__main__":
    asyncio.run(main())