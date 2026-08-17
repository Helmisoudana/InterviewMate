class TTSSession:

    def __init__(self, session_id, voice: str) -> None:
        self.session_id = session_id
        self.voice = voice