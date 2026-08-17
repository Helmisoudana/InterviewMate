

class TTSSessionRegistry:
    def __init__(self) -> None:
        self._sessions: dict = {}

    def enregistrer(self, session) -> None:
        self._sessions[session.session_id.value] = session

    def obtenir(self, session_id):
        return self._sessions.get(session_id.value)

    def retirer(self, session_id) -> None:
        self._sessions.pop(session_id.value, None)