from gateway.domain.ports.storage_client_port import ScoringClientPort
from scoring.domain.entities.rapport_score import RapportScore
from scoring.application.use_cases.generer_rapport_session import GenererRapportSessionUseCase


class InProcessScoringClient(ScoringClientPort):
    """Appel direct en process (pas de reseau), meme pattern que InProcessAgentClient/InProcessASRClient/InProcessTTSClient."""

    def __init__(self, generer_rapport_uc: GenererRapportSessionUseCase):
        self._generer_rapport_uc = generer_rapport_uc

    async def cloturer_session(self, session_id: str) -> RapportScore:
        return await self._generer_rapport_uc.executer(session_id)