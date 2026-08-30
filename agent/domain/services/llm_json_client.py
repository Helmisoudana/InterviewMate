import json
import logging
from agent.domain.ports.llm_port import LLMPort
from agent.domain.value_objects.message import Message
from shared.domain.exceptions import ReponseLLMInvalide
logger = logging.getLogger("llm_json_client")





SCHEMA_REPONSE = {
    "type": "object",
    "properties": {
        "question": {"type": "string"},
        "qualite_reponse_precedente": {
            "type": "string",
            "enum": ["faible", "correcte", "excellente"],
        },
        "difficulte_suivante": {
            "type": "string",
            "enum": ["facile", "moyen", "difficile"],
        },
        "changement_phase": {"type": "boolean"},
        "phase_suivante": {"type": "string"},
        "comportement_inapproprie": {"type": "boolean"},
        "entretien_termine": {"type": "boolean"},
    },
    "required": [
        "question",
        "difficulte_suivante",
        "changement_phase",
        "comportement_inapproprie",
        "entretien_termine",
    ],
}


async def _generer(llm: LLMPort, messages: list[Message]) -> str:
    texte = ""
    async for token in llm.stream_completion(messages, response_schema=SCHEMA_REPONSE):
        texte += token
    return texte


async def appeler_llm_json(llm: LLMPort, messages: list[Message]) -> dict:
    for tentative in range(2):
        texte = await _generer(llm, messages)
        try:
            resultat = json.loads(texte)
        except json.JSONDecodeError:
            logger.warning(
                "Tentative %d/2 : réponse LLM non-JSON malgré le schéma structuré : %r",
                tentative + 1, texte[:300],
            )
            continue

        if isinstance(resultat, dict) and isinstance(resultat.get("question"), str):
            return resultat

        logger.warning(
            "Tentative %d/2 : JSON valide mais forme inattendue : %r",
            tentative + 1, resultat,
        )

    raise ReponseLLMInvalide(
        "Le LLM n'a pas produit de réponse exploitable après 2 tentatives."
    )