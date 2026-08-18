from agent.infrastructure.adapters.session_registry import AgentSessionRegistry
from shared.domain import SessionID


class EndAgentSessionUseCase:
    def __init__(self, registry: AgentSessionRegistry) -> None:
        self._registry = registry

    async def executer(self, session_id: SessionID) -> None:
        self._registry.retirer(session_id.value)
