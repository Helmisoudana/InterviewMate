from agent.domain.entities.echange import Echange
from agent.domain.services.system_prompt_builder import construire_prompt_systeme
from agent.domain.services.llm_json_client import appeler_llm_json
from agent.domain.ports.llm_port import LLMPort
from agent.domain.ports.Storage_notifier_port import StorageNotifierPort
from agent.domain.value_objects.message import Message
from agent.domain.value_objects.interview_phase import InterviewPhase, DifficultyLevel
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry
from shared.domain import SessionID


class ConduireEntretienUseCase:
    def __init__(
        self,
        llm: LLMPort,
        registry: AgentSessionRegistry,
        storage_notifier: StorageNotifierPort | None = None,
    ):
        self.llm = llm
        self.registry = registry
        self.storage_notifier = storage_notifier

    async def traiter_reponse_candidat(self, session_id: SessionID | str, texte_reponse: str) -> tuple[str, bool]:
        session_id_str = session_id.value if isinstance(session_id, SessionID) else session_id
        interview = self.registry.obtenir(session_id_str)

        if interview.echanges:
            interview.echanges[-1].reponse = texte_reponse

        prompt_systeme = construire_prompt_systeme(interview)
        messages = [
            Message(role="system", content=prompt_systeme),
            Message(role="user", content=texte_reponse),
        ]
        resultat = await appeler_llm_json(self.llm, messages)

        if interview.echanges and self.storage_notifier is not None:
            await self.storage_notifier.notifier_echange_termine(session_id_str, interview.echanges[-1])

        interview.difficulte_actuelle = DifficultyLevel(
            resultat.get("difficulte_suivante", interview.difficulte_actuelle.value)
        )

        if resultat.get("changement_phase") and resultat.get("phase_suivante"):
            interview.phase_actuelle = InterviewPhase(resultat["phase_suivante"])

        if resultat.get("entretien_termine"):
            self.registry.sauvegarder(session_id_str, interview)
            return "", True

        nouvelle_question = resultat.get("question", "")
        interview.echanges.append(Echange(question=nouvelle_question, phase=interview.phase_actuelle))
        self.registry.sauvegarder(session_id_str, interview)

        return nouvelle_question, False