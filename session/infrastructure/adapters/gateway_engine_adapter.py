from session.domain.value_objects.session_id import SessionId as SessionModuleId
from session.domain.value_objects.session_config import SessionConfig
from session.application.use_cases.create_session import CreateSessionUseCase
from session.application.use_cases.get_session_state import GetSessionStateUseCase
from session.domain.exceptions.exceptions import SessionInconnueError
from session.infrastructure.adapters.in_memory_session_store import InMemorySessionStore


CONFIG_PAR_DEFAUT = SessionConfig(
    type_entretien="technique",
    niveau="confirme",
    poste_vise="Non précisé",
    duree_max_minutes=30,
)


class SessionGatewayEngineAdapter:
    

    def __init__(
        self,
        store: InMemorySessionStore,
        create_session: CreateSessionUseCase,
        get_state: GetSessionStateUseCase,
    ) -> None:
        self._store = store
        self._create_session = create_session
        self._get_state = get_state

    async def valider_session(self, session_id) -> bool:
        module_id = SessionModuleId(session_id.value)
        try:
            self._get_state.executer(module_id)
            return True
        except SessionInconnueError:
            # Provisionnement automatique : voir CONFIG_PAR_DEFAUT ci-dessus.
            nouvelle_session = self._create_session.executer(module_id, CONFIG_PAR_DEFAUT)
            self._store.enregistrer(nouvelle_session)
            return True

    async def notifier_coupure(self, session_id, raison: str) -> None:
        module_id = SessionModuleId(session_id.value)
        session = self._store.obtenir(module_id)
        if session is not None:
            session.enregistrer_activite()

    async def notifier_reconnexion(self, session_id) -> None:
        module_id = SessionModuleId(session_id.value)
        session = self._store.obtenir(module_id)
        if session is not None:
            session.enregistrer_activite()