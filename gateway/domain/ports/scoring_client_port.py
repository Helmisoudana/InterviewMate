from abc import ABC, abstractmethod
from scoring.domain.entities.rapport_score import RapportScore


class ScoringClientPort(ABC):
    """Port sortant du gateway vers le module scoring, symetrique a AgentClientPort/ASRClientPort/TTSClientPort."""

    @abstractmethod
    async def cloturer_session(self, session_id: str) -> RapportScore:
        pass