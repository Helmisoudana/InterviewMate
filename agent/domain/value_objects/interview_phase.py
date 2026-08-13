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