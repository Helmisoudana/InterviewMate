from domain.value_objects.session_id import SessionId


class FakeTTSClient:
    def __init__(self) -> None:
        self.textes_demandes: list[str] = []

    async def demander_synthese(self, session_id: SessionId, texte: str) -> None:
        self.textes_demandes.append(texte)