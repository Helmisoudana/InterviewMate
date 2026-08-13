from agent.domain.ports.session_repository_port import SessionRepositoryPort
from agent.domain.entities.interview import Interview


class FakeSessionRepositoryAdapter(SessionRepositoryPort):
    def __init__(self):
        self._store: dict[str, Interview] = {}

    async def get(self, session_id: str) -> Interview:
        return self._store.get(session_id, Interview())

    async def save(self, session_id: str, interview: Interview) -> None:
        self._store[session_id] = interview