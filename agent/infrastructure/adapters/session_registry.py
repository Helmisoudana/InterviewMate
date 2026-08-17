from agent.domain.entities.interview import Interview


class AgentSessionRegistry:
    def __init__(self) -> None:
        self._sessions: dict[str, Interview] = {}

    def enregistrer(self, session_id: str, interview: Interview) -> None:
        self._sessions[session_id] = interview

    def obtenir(self, session_id: str) -> Interview | None:
        return self._sessions.get(session_id)

    def retirer(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)