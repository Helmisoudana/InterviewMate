from enum import Enum


class InterviewPhase(Enum):
    INTRO = "intro"
    PRESENTATION = "presentation"
    COMPETENCES = "competences"
    POSTE = "poste"
    CLOTURE = "cloture"


class DifficultyLevel(Enum):
    FACILE = "facile"
    MOYEN = "moyen"
    DIFFICILE = "difficile"


class DureeEntretien(Enum):
    COURTE = "courte"
    MOYENNE = "moyenne"
    LONGUE = "longue"


ORDRE_PHASES = [
    InterviewPhase.INTRO,
    InterviewPhase.PRESENTATION,
    InterviewPhase.COMPETENCES,
    InterviewPhase.POSTE,
    InterviewPhase.CLOTURE,
]

QUESTIONS_PAR_DUREE = {
    DureeEntretien.COURTE: {
        InterviewPhase.INTRO: 1,
        InterviewPhase.PRESENTATION: 1,
        InterviewPhase.COMPETENCES: 2,
        InterviewPhase.POSTE: 1,
        InterviewPhase.CLOTURE: 1,
    },
    DureeEntretien.MOYENNE: {
        InterviewPhase.INTRO: 1,
        InterviewPhase.PRESENTATION: 1,
        InterviewPhase.COMPETENCES: 4,
        InterviewPhase.POSTE: 2,
        InterviewPhase.CLOTURE: 1,
    },
    DureeEntretien.LONGUE: {
        InterviewPhase.INTRO: 1,
        InterviewPhase.PRESENTATION: 2,
        InterviewPhase.COMPETENCES: 6,
        InterviewPhase.POSTE: 3,
        InterviewPhase.CLOTURE: 1,
    },
}