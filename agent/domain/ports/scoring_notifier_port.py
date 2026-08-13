# agent/domain/ports/scoring_notifier_port.py
from abc import ABC, abstractmethod
from agent.domain.entities.interview import Echange


class ScoringNotifierPort(ABC):
    @abstractmethod
    async def notifier_echange_termine(self, session_id: str, echange: Echange) -> None:
        ...