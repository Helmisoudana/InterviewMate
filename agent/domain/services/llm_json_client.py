import json
import logging
import re
from agent.domain.ports.llm_port import LLMPort
from agent.domain.value_objects.message import Message

logger = logging.getLogger("llm_json_client")

RESULTAT_PAR_DEFAUT = {
    "question": "",
    "difficulte_suivante": "moyen",
    "changement_phase": False,
    "phase_suivante": None,
    "comportement_inapproprie": False,
    "entretien_termine": False,
}

MESSAGE_SECOURS = (
    "Pouvez-vous reformuler ou préciser votre réponse, s'il vous plaît ?"
)

_BLOC_CODE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
_PREMIER_OBJET = re.compile(r"\{.*\}", re.DOTALL)
_CHAMP_QUESTION = re.compile(r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"', re.DOTALL)


def _nettoyer(texte: str) -> str:
    match = _BLOC_CODE.search(texte)
    return match.group(1) if match else texte


def _extraire_json(texte: str) -> dict | None:
    candidats = [texte, _nettoyer(texte)]
    match_objet = _PREMIER_OBJET.search(texte)
    if match_objet:
        candidats.append(match_objet.group(0))

    for candidat in candidats:
        try:
            return json.loads(candidat)
        except json.JSONDecodeError:
            continue

    reparation = texte.rstrip()
    if reparation.count('"') % 2 == 1:
        reparation += '"'
    ouvertes = reparation.count("{") - reparation.count("}")
    if ouvertes > 0:
        reparation += "}" * ouvertes
        try:
            return json.loads(reparation)
        except json.JSONDecodeError:
            pass
    return None


async def appeler_llm_json(llm: LLMPort, messages: list[Message]) -> dict:
    texte = ""
    async for token in llm.stream_completion(messages):
        texte += token

    resultat = _extraire_json(texte)
    if resultat is not None and isinstance(resultat.get("question"), str):
        return resultat


    logger.warning("Réponse LLM non-JSON ou incomplète, tentative d'extraction ciblée : %r", texte[:300])
    match_question = _CHAMP_QUESTION.search(texte)
    resultat = dict(RESULTAT_PAR_DEFAUT)
    if match_question:
        try:
            resultat["question"] = json.loads(f'"{match_question.group(1)}"')
        except json.JSONDecodeError:
            resultat["question"] = MESSAGE_SECOURS
    else:
        resultat["question"] = MESSAGE_SECOURS
    return resultat