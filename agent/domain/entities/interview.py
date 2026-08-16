from dataclasses import dataclass, field
from datetime import datetime
from agent.domain.value_objects.interview_phase import InterviewPhase, DifficultyLevel


@dataclass
class Question:
    texte: str
    phase: InterviewPhase
    horodatage: datetime = field(default_factory=datetime.now)


@dataclass
class Reponse:
    texte: str
    qualite_percue: str | None = None  # "vague", "correcte", "excellente" — ou None si pas encore evaluee


@dataclass
class Echange:
    question: Question
    reponse: Reponse | None = None  # None tant que le candidat n'a pas encore repondu


# Combien de questions on pose avant de changer de phase
QUESTIONS_PAR_PHASE = {
    InterviewPhase.INTRO: 1,
    InterviewPhase.TECHNIQUE: 4,
    InterviewPhase.COMPORTEMENTAL: 2,
    InterviewPhase.CLOTURE: 1,
}

# L'ordre dans lequel les phases s'enchainent
ORDRE_PHASES = [
    InterviewPhase.INTRO,
    InterviewPhase.TECHNIQUE,
    InterviewPhase.COMPORTEMENTAL,
    InterviewPhase.CLOTURE,
]


def evaluer_qualite_reponse(texte_reponse: str) -> str:
    texte = texte_reponse.strip().lower()
    mots_vagues = ["je ne sais pas", "peut-etre", "je pense que", "pas sur", "aucune idee"]

    if len(texte) < 20 or any(mot in texte for mot in mots_vagues):
        return "vague"
    if len(texte) > 150:
        return "excellente"
    return "correcte"


@dataclass
class Interview:
    phase_actuelle: InterviewPhase = InterviewPhase.INTRO
    difficulte_actuelle: DifficultyLevel = DifficultyLevel.MOYEN
    langue: str = "francais"
    echanges: list[Echange] = field(default_factory=list)

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

    def vers_prompt_systeme(self) -> str:
        historique = "\n".join(f"- {q}" for q in self.questions_deja_posees()) or "Aucune question posee pour le moment."
        instruction_langue = (
            "Tu dois repondre UNIQUEMENT en francais, sans aucun mot d'anglais."
            if self.langue == "francais"
            else "You must respond ONLY in English, no other language."
        )
        return (
            f"Tu es un recruteur technique qui mene un entretien d'embauche.\n\n"
            f"{instruction_langue}\n\n"
            f"Phase actuelle : {self.phase_actuelle.value}\n"
            f"Niveau de difficulte : {self.difficulte_actuelle.value}\n\n"
            f"Questions deja posees (ne jamais les reposer) :\n{historique}\n\n"
            f"Pose UNE seule question, adaptee a la phase et au niveau de difficulte actuels.\n"
            f"Reponds uniquement avec le texte de la question, sans autre commentaire."
        )