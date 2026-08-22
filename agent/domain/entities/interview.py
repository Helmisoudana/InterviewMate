from dataclasses import dataclass, field
from agent.domain.value_objects.interview_phase import (
    InterviewPhase,
    DifficultyLevel,
    DureeEntretien,
    QUESTIONS_PAR_DUREE,
)
from agent.domain.entities.echange import Echange


@dataclass
class Interview:
    poste: str
    langue: str
    duree: DureeEntretien
    phase_actuelle: InterviewPhase = InterviewPhase.INTRO
    difficulte_actuelle: DifficultyLevel = DifficultyLevel.MOYEN
    echanges: list[Echange] = field(default_factory=list)

    @property
    def nb_questions_par_phase(self) -> dict[InterviewPhase, int]:
        return QUESTIONS_PAR_DUREE[self.duree]