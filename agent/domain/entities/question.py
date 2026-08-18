from dataclasses import dataclass, field
from datetime import datetime
from agent.domain.value_objects.interview_phase import InterviewPhase


@dataclass
class Question:
    texte: str
    phase: InterviewPhase
    horodatage: datetime = field(default_factory=datetime.now)