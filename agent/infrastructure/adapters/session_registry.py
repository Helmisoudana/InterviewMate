class AgentSessionRegistry:
    def __init__(self) -> None:
        self._sessions_actives: set[str] = set()

    def enregistrer(self, session_id: str) -> None:
        self._sessions_actives.add(session_id)

    def est_active(self, session_id: str) -> bool:
        return session_id in self._sessions_actives

    def retirer(self, session_id: str) -> None:
        self._sessions_actives.discard(session_id)