
from shared.domain import InterviewStage as InterviewPhase
from shared.domain.value_objects import QUESTIONS_PAR_STAGE as QUESTIONS_PAR_PHASE
from shared.domain.value_objects import ORDRE_STAGES as ORDRE_PHASES
from enum import Enum


class DifficultyLevel(Enum):
    FACILE = "facile"
    MOYEN = "moyen"
    DIFFICILE = "difficile"
