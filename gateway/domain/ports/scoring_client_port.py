from abc import ABC, abstractmethod
from scoring.domain.entities.rapport_score import RapportScore


class ScoringClientPort(ABC):
    @abstractmethod
    async def cloturer_session(self, session_id: str) -> RapportScore:
        pass