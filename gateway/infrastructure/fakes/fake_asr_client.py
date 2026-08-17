from domain.value_objects.session_id import SessionId
from domain.value_objects.audio_chunk import AudioChunk


class FakeASRClient:
    def __init__(self) -> None:
        self.chunks_recus: list[AudioChunk] = []
        self.fins_de_tour: list[SessionId] = []

    async def envoyer_chunk(self, session_id: SessionId, chunk: AudioChunk) -> None:
        self.chunks_recus.append(chunk)

    async def signaler_fin_de_tour(self, session_id: SessionId) -> None:
        self.fins_de_tour.append(session_id)