from agent.domain.entities.interview import Interview
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry
from shared.domain import SessionID


class EndAgentSessionUseCase:
    def __init__(self, registry: AgentSessionRegistry) -> None:
        self._registry = registry

    async def executer(self, session_id: SessionID) -> Interview:
        interview = self._registry.obtenir(session_id.value)
        self._registry.retirer(session_id.value)
        return interview