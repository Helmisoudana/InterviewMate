from dataclasses import dataclass, field
from agent.domain.value_objects.interview_phase import (
    InterviewPhase,
    DifficultyLevel,
    QUESTIONS_PAR_PHASE,
    ORDRE_PHASES,
)
from agent.domain.entities.echange import Echange


@dataclass
class Interview:
    phase_actuelle: InterviewPhase = InterviewPhase.INTRO
    difficulte_actuelle: DifficultyLevel = DifficultyLevel.MOYEN
    langue: str = "francais"
    persona: str = "bienveillant"
    echanges: list[Echange] = field(default_factory=list)
    nb_refus_consecutifs: int = 0

    def signaler_refus(self) -> None:
        self.nb_refus_consecutifs += 1

    def reinitialiser_refus(self) -> None:
        self.nb_refus_consecutifs = 0

    def doit_arreter_anticipativement(self) -> bool:
        return self.nb_refus_consecutifs >= 2

    def questions_deja_posees(self) -> list[str]:
        return [e.question.texte for e in self.echanges]

    def peut_poser_question(self, texte_question: str) -> bool:
        return texte_question not in self.questions_deja_posees()

    def nb_questions_phase_actuelle(self) -> int:
        return sum(1 for e in self.echanges if e.question.phase == self.phase_actuelle)

    def doit_changer_de_phase(self) -> bool:
        seuil = QUESTIONS_PAR_PHASE[self.phase_actuelle]
        return self.nb_questions_phase_actuelle() >= seuil

    def passer_phase_suivante(self) -> None:
        idx_actuel = ORDRE_PHASES.index(self.phase_actuelle)
        if idx_actuel + 1 < len(ORDRE_PHASES):
            self.phase_actuelle = ORDRE_PHASES[idx_actuel + 1]

    def est_terminee(self) -> bool:
        return self.phase_actuelle == InterviewPhase.CLOTURE and self.doit_changer_de_phase()

    def ajuster_difficulte(self, qualite_derniere_reponse: str) -> None:
        if qualite_derniere_reponse == "vague":
            if self.difficulte_actuelle == DifficultyLevel.DIFFICILE:
                self.difficulte_actuelle = DifficultyLevel.MOYEN
            elif self.difficulte_actuelle == DifficultyLevel.MOYEN:
                self.difficulte_actuelle = DifficultyLevel.FACILE
        elif qualite_derniere_reponse == "excellente":
            if self.difficulte_actuelle == DifficultyLevel.FACILE:
                self.difficulte_actuelle = DifficultyLevel.MOYEN
            elif self.difficulte_actuelle == DifficultyLevel.MOYEN:
                self.difficulte_actuelle = DifficultyLevel.DIFFICILE