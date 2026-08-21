from shared.domain.value_objects import SessionID
from storage.domain.ports.transcript_repository_port import TranscriptRepositoryPort
from storage.domain.ports.rapport_repository_port import RapportRepositoryPort


class InMemoryStorageAdapter(TranscriptRepositoryPort, RapportRepositoryPort):
    def __init__(self):
        self._transcripts: dict[str, dict] = {}
        self._rapports: dict[str, dict] = {}

    async def sauvegarder_transcript(self, session_id: SessionID, transcript: dict) -> None:
        self._transcripts[str(session_id)] = transcript

    async def recuperer_historique(self, user_id: str) -> list[dict]:
        return list(self._transcripts.values())

    async def sauvegarder_rapport(self, session_id: SessionID, rapport: dict) -> None:
        self._rapports[str(session_id)] = rapport

    async def recuperer_rapport(self, session_id: SessionID) -> dict | None:
        return self._rapports.get(str(session_id))