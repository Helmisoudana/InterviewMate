import asyncio

from  domain.value_objects.session_id import SessionId
from  domain.value_objects.audio_chunk import AudioChunk
from  infrastructure.adapters.in_process_asr_client import InProcessASRClient
from  infrastructure.adapters.in_process_tts_client import InProcessTTSClient
from  infrastructure.engines.stub_asr_engine import StubASREngine
from  infrastructure.engines.stub_tts_engine import StubTTSEngine


async def main():
    session_id = SessionId("demo-001")

    asr_client = InProcessASRClient(StubASREngine())
    resultats_recus = []
    asr_client.souscrire_resultats(session_id, callback=lambda r: resultats_recus.append(r) or asyncio.sleep(0))

    chunk = AudioChunk(data=b"\x00" * 320, sequence_number=1)
    await asr_client.envoyer_chunk(session_id, chunk)
    await asr_client.signaler_fin_de_tour(session_id)
    print(resultats_recus)  # [partial, final]

    tts_client = InProcessTTSClient(StubTTSEngine())
    async for audio_bytes in tts_client.synthetiser_stream(session_id, "Bonjour"):
        print(f"chunk reçu : {len(audio_bytes)} octets")

asyncio.run(main())