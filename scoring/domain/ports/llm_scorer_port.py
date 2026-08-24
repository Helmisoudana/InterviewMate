from abc import ABC, abstractmethod
from typing import List
from scoring.domain.entities.rapport_score import RapportScore
class LLMScorerPort(ABC):
    @abstractmethod
    async def generer_rapport(self, session_id: str, echanges: List[dict]) -> RapportScore:
        pass