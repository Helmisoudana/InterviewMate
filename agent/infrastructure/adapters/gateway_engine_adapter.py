from agent.application.use_cases.conduire_entretien import ConduireEntretienUseCase
from agent.domain.entities.interview import Interview
from agent.domain.ports.llm_port import LLMPort
from agent.domain.ports.session_repository_port import SessionRepositoryPort
from agent.domain.ports.scoring_notifier_port import ScoringNotifierPort
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry


class AgentGatewayEngineAdapter:
    def __init__(
        self,
        registry: AgentSessionRegistry,
        llm: LLMPort,
        session_repo: SessionRepositoryPort,
        scoring_notifier: ScoringNotifierPort,
    ) -> None:
        self._registry = registry
        self._session_repo = session_repo
        self._conduire = ConduireEntretienUseCase(llm=llm, session_repo=session_repo, scoring_notifier=scoring_notifier)

    async def demarrer_session(self, session_id: str) -> None:
        interview = Interview()
        self._registry.enregistrer(session_id, interview)
        await self._session_repo.save(session_id, interview)

    async def traiter_reponse(self, session_id: str, texte_reponse: str) -> tuple[str, bool]:
        self._obtenir_session(session_id)
        return await self._conduire.traiter_reponse_candidat(session_id, texte_reponse)

    async def terminer_session(self, session_id: str) -> None:
        self._obtenir_session(session_id)
        self._registry.retirer(session_id)

    def _obtenir_session(self, session_id: str) -> Interview:
        interview = self._registry.obtenir(session_id)
        if interview is None:
            raise ValueError(f"Session Agent inconnue : {session_id}")
        return interview