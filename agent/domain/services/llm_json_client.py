import json
from agent.domain.ports.llm_port import LLMPort
from agent.domain.value_objects.message import Message

RESULTAT_PAR_DEFAUT = {
    "question": "",
    "difficulte_suivante": "moyen",
    "changement_phase": False,
    "phase_suivante": None,
    "comportement_inapproprie": False,
    "entretien_termine": False,
}


async def appeler_llm_json(llm: LLMPort, messages: list[Message]) -> dict:
    texte = ""
    async for token in llm.stream_completion(messages):
        texte += token
    try:
        return json.loads(texte)
    except json.JSONDecodeError:
        resultat = dict(RESULTAT_PAR_DEFAUT)
        resultat["question"] = texte.strip()
        return resultat