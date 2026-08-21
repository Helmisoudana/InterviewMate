from shared.domain.value_objects import EchangeEvalue

GRILLE_PAR_DEFAUT = ["clarte_communication", "rigueur_technique", "resolution_de_probleme"]


def construire_prompt_evaluation(echange: EchangeEvalue, grille_competences: list[str] | None = None) -> str:
    grille = grille_competences or GRILLE_PAR_DEFAUT
    competences_str = ", ".join(grille)

    return f"""### ROLE ###
Tu es un evaluateur technique senior charge de noter objectivement la reponse
d'un candidat lors d'un entretien d'embauche.

### ECHANGE A EVALUER ###
Question posee : {echange.question}
Reponse du candidat : {echange.reponse}

### COMPETENCES A EVALUER (choisis la plus pertinente pour cet echange) ###
{competences_str}

### TA MISSION ###
1. Choisis UNE seule competence dans la liste ci-dessus, la plus pertinente pour juger cet echange.
2. Attribue un score entre 0.0 (tres faible) et 1.0 (excellent).
3. Justifie ce score en une phrase courte, factuelle, sans jugement de valeur inutile.

### FORMAT DE SORTIE OBLIGATOIRE ###
Reponds UNIQUEMENT avec un objet JSON valide, rien d'autre avant ou apres.
Exemple : {{"competence": "rigueur_technique", "score": 0.75, "justification": "Reponse precise mais incomplete sur les cas limites."}}

### RAPPELS CRITIQUES ###
- Le champ "competence" doit etre exactement l'une des valeurs listees ci-dessus.
- Le champ "score" doit etre un nombre entre 0.0 et 1.0.
- Aucun texte en dehors de l'objet JSON, sous aucun pretexte."""