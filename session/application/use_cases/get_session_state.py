from shared.domain import SessionID, stage_to_public_phase
from shared.contracts.dtos import SessionStateDTO
from session.domain.exceptions.exceptions import SessionInconnueError
from session.domain.ports.session_repository_port import SessionRepositoryPort
from session.domain.value_objects.phase import Phase


class GetSessionStateUseCase:
    def __init__(self, store: SessionRepositoryPort) -> None:
        self._store = store

    def executer(self, session_id: SessionID) -> SessionStateDTO:
        session = self._store.obtenir(session_id)
        if session is None:
            raise SessionInconnueError(f"Session {session_id.value} inconnue")
        
        phase_mapped = stage_to_public_phase(session.phase)
        history_mapped = [
            {"question": exchange.question, "reponse": exchange.reponse}
            for exchange in session.historique
        ]
        
        return SessionStateDTO(
            session_id=session_id,
            phase=phase_mapped,
            history=history_mapped,
            is_active=session.phase != Phase.TERMINEE
        )