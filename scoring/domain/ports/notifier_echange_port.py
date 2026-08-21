from abc import ABC, abstractmethod
from shared.domain.value_objects import EchangeEvalue
from scoring.domain.entities.evaluation import Evaluation


class NotifierEchangeUseCasePort(ABC):
    @abstractmethod
    async def executer(self, echange: EchangeEvalue) -> Evaluation:
        ...