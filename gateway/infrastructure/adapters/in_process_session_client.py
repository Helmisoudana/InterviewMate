from gateway.domain.ports.session_client_port import SessionClientPort
from shared.domain import SessionID
from session.application.use_cases.create_session import CreateSessionUseCase
from session.application.use_cases.get_session_state import GetSessionStateUseCase
from session.domain.exceptions.exceptions import SessionInconnueError
from session.domain.value_objects.session_config import SessionConfig


CONFIG_PAR_DEFAUT = SessionConfig(
    type_entretien="technique",
    niveau="confirme",
    poste_vise="Developpeur Python",
    duree_max_minutes=30
)


class InProcessSessionClient(SessionClientPort):
    def __init__(
        self,
        create_uc: CreateSessionUseCase,
        get_state_uc: GetSessionStateUseCase,
        store
    ) -> None:
        self._create_uc = create_uc
        self._get_state_uc = get_state_uc
        self._store = store

    async def valider_session(self, session_id: SessionID) -> bool:
        try:
            self._get_state_uc.executer(session_id)
            return True
        except SessionInconnueError:
            self._create_uc.executer(session_id, CONFIG_PAR_DEFAUT)
            return True

    async def notifier_coupure(self, session_id: SessionID, raison: str) -> None:
        session = self._store.obtenir(session_id)
        if session is not None:
            session.enregistrer_activite()

    async def notifier_reconnexion(self, session_id: SessionID) -> None:
        session = self._store.obtenir(session_id)
        if session is not None:
            session.enregistrer_activite()
