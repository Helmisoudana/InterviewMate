from shared.domain import SessionID
from session.domain.value_objects.phase import Phase
from session.domain.ports.session_repository_port import SessionRepositoryPort
from session.domain.exceptions.exceptions import SessionInconnueError


class UpdateSessionStateUseCase:
    def __init__(self, store: SessionRepositoryPort) -> None:
        self._store = store

    def executer(
        self,
        session_id: SessionID,
        question: str,
        reponse: str,
        nouvelle_phase: Phase | None = None
    ) -> None:
        session = self._store.obtenir(session_id)
        if session is None:
            raise SessionInconnueError(f"Session {session_id.value} inconnue")
        
        session.ajouter_echange(question, reponse)
        if nouvelle_phase is not None:
            session.changer_phase(nouvelle_phase)
            
        self._store.enregistrer(session)