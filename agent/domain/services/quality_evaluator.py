MOTS_VAGUES = ["je ne sais pas", "peut-etre", "je pense que", "pas sur", "aucune idee"]


def evaluer_qualite_reponse(texte_reponse: str) -> str:
    texte = texte_reponse.strip().lower()

    if len(texte) < 20 or any(mot in texte for mot in MOTS_VAGUES):
        return "vague"
    if len(texte) > 150:
        return "excellente"
    return "correcte"