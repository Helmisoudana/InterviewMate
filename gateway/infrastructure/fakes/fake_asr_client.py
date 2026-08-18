from shared.domain import SessionID, AudioChunk


class FakeASRClient:
    def __init__(self) -> None:
        self.chunks_recus: list[AudioChunk] = []
        self.fins_de_tour: list[SessionID] = []

    async def envoyer_chunk(self, session_id: SessionID, chunk: AudioChunk) -> None:
        self.chunks_recus.append(chunk)

    async def signaler_fin_de_tour(self, session_id: SessionID) -> None:
        self.fins_de_tour.append(session_id)