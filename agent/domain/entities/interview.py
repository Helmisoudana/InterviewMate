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
    qualite_percue: str | None = None


@dataclass
class Echange:
    question: Question
    reponse: Reponse | None = None


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
    persona: str = "bienveillant"
    echanges: list[Echange] = field(default_factory=list)
    nb_refus_consecutifs: int = 0

    def signaler_refus(self) -> None:
        self.nb_refus_consecutifs += 1

    def reinitialiser_refus(self) -> None:
        self.nb_refus_consecutifs = 0

    def doit_arreter_anticipativement(self) -> bool:
        return self.nb_refus_consecutifs >= 2

    # Puis le reste de tes méthodes
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
            "Tu dois t'exprimer exclusivement en francais, avec un vocabulaire naturel et professionnel."
            if self.langue == "francais"
            else "You must express yourself exclusively in English, with natural and professional vocabulary."
        )

        tons_persona = {
            "bienveillant": "Ton style est chaleureux, encourageant, tu mets le candidat en confiance sans jamais perdre ton exigence professionnelle.",
            "exigeant": "Ton style est direct et rigoureux, tu challenges le candidat avec des questions precises et sans complaisance.",
            "neutre": "Ton style est professionnel, factuel, sans emotion superflue.",
        }
        instruction_ton = tons_persona.get(self.persona, tons_persona["neutre"])

        return f"""### ROLE ###
Tu incarnes un recruteur technique senior menant un entretien d'embauche en temps reel.
{instruction_ton}
{instruction_langue}

### CONTEXTE ACTUEL DE L'ENTRETIEN ###
Phase : {self.phase_actuelle.value}
Niveau de difficulte : {self.difficulte_actuelle.value}
Questions deja posees (interdiction absolue de les reposer sous une forme identique ou reformulee) :
{historique}

### TA MISSION A CHAQUE TOUR ###
1. Analyse la reponse du candidat que tu viens de recevoir.
2. Juge sa qualite avec exigence : une reponse vague, evasive ou trop courte est "vague" ;
   une reponse solide et argumentee est "correcte" ; une reponse qui demontre une vraie
   maitrise et va au-dela de l'attendu est "excellente".
3. Detecte si le message contient un comportement inapproprie (insultes, propos
   deplaces, hors-sujet volontaire, contenu choquant).
4. Formule UNE seule question suivante, pertinente, adaptee a la phase et a la
   difficulte actuelles, qui fait progresser naturellement l'entretien.

### FORMAT DE SORTIE OBLIGATOIRE ###
Reponds UNIQUEMENT avec un objet JSON valide, rien d'autre avant ou apres,
aucune phrase d'introduction, aucun commentaire. Exemple de format attendu :

{{"qualite": "correcte", "comportement_inapproprie": false, "question": "Pouvez-vous decrire un defi technique que vous avez recemment resolu ?"}}

### RAPPELS CRITIQUES ###
- Le champ "qualite" doit etre exactement "vague", "correcte" ou "excellente".
- Le champ "comportement_inapproprie" doit etre un booleen true ou false, jamais une chaine.
- Aucun texte en dehors de l'objet JSON, sous aucun pretexte."""