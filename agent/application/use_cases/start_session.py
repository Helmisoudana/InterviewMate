from agent.domain.entities.interview import Interview
from agent.domain.ports.session_repository_port import SessionRepositoryPort
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry
from shared.domain import SessionID


class StartAgentSessionUseCase:
    def __init__(self, session_repo: SessionRepositoryPort, registry: AgentSessionRegistry) -> None:
        self._session_repo = session_repo
        self._registry = registry

    async def executer(self, session_id: SessionID) -> None:
        self._registry.enregistrer(session_id.value)
        await self._session_repo.save(session_id.value, Interview())
