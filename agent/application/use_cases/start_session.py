from agent.domain.entities.interview import Interview
from agent.domain.entities.echange import Echange
from agent.domain.ports.llm_port import LLMPort
from agent.domain.services.system_prompt_builder import construire_prompt_systeme
from agent.domain.services.llm_json_client import appeler_llm_json
from agent.domain.value_objects.interview_phase import DureeEntretien, DifficultyLevel
from agent.domain.value_objects.message import Message
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry
from shared.domain import SessionID


class StartAgentSessionUseCase:
    def __init__(self, llm: LLMPort, registry: AgentSessionRegistry) -> None:
        self._llm = llm
        self._registry = registry

    async def executer(
        self,
        session_id: SessionID,
        poste: str,
        langue: str,
        duree: DureeEntretien,
        difficulte: DifficultyLevel = DifficultyLevel.MOYEN,
    ) -> str:
        interview = Interview(
            poste=poste,
            langue=langue,
            duree=duree,
            difficulte_actuelle=difficulte,
        )

        prompt_systeme = construire_prompt_systeme(interview)
        messages = [
            Message(role="system", content=prompt_systeme),
            Message(role="user", content="(Début de la session, aucune réponse du candidat pour l'instant.)"),
        ]
        resultat = await appeler_llm_json(self._llm, messages)

        message_bienvenue = resultat.get("question", "")
        interview.echanges.append(Echange(question=message_bienvenue, phase=interview.phase_actuelle))

        self._registry.enregistrer(session_id.value, interview)

        return message_bienvenue