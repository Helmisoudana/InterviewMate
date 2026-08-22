from abc import ABC, abstractmethod
from shared.domain import SessionID
from agent.domain.entities.interview import Interview
from agent.domain.value_objects.interview_phase import DureeEntretien, DifficultyLevel


class AgentClientPort(ABC):
    @abstractmethod
    async def demarrer_session(
        self,
        session_id: SessionID,
        poste: str,
        langue: str,
        duree: DureeEntretien,
        difficulte: DifficultyLevel = DifficultyLevel.MOYEN,
    ) -> str:
        ...

    @abstractmethod
    async def traiter_reponse(self, session_id: SessionID, texte_reponse: str) -> tuple[str, bool]:
        ...

    @abstractmethod
    async def terminer_session(self, session_id: SessionID) -> Interview:
        ...