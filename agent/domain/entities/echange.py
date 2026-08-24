from dataclasses import dataclass, field
from datetime import datetime
from agent.domain.value_objects.interview_phase import InterviewPhase


@dataclass
class Echange:
    question: str
    phase: InterviewPhase
    reponse: str | None = None
    qualite: str | None = None 