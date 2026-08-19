from dataclasses import dataclass
from agent.domain.entities.question import Question
from agent.domain.entities.reponse import Reponse


@dataclass
class Echange:
    question: Question
    reponse: Reponse | None = None