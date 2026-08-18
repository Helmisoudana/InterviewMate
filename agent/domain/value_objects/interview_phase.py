from enum import Enum


class InterviewPhase(Enum):
    INTRO = "intro"
    TECHNIQUE = "technique"
    COMPORTEMENTAL = "comportemental"
    CLOTURE = "cloture"


class DifficultyLevel(Enum):
    FACILE = "facile"
    MOYEN = "moyen"
    DIFFICILE = "difficile"


QUESTIONS_PAR_PHASE = {
    InterviewPhase.INTRO: 1,
    InterviewPhase.TECHNIQUE: 4,
    InterviewPhase.COMPORTEMENTAL: 2,
    InterviewPhase.CLOTURE: 1,
}

ORDRE_PHASES = [
    InterviewPhase.INTRO,
    InterviewPhase.TECHNIQUE,
    InterviewPhase.COMPORTEMENTAL,
    InterviewPhase.CLOTURE,
]