from __future__ import annotations

from domain.value_objects.session_id import SessionId
from domain.value_objects.enums import ConnectionState, TurnState

from domain.exceptions.exceptions import SessionFermeeError , SessionNonActiveError

class GatewaySession:
    

    def __init__(self, session_id: SessionId) -> None:
        self.session_id = session_id
        self.connection_state = ConnectionState.CONNECTING
        self.turn_state = TurnState.SILENT

    def activer(self) -> None:
        self.connection_state = ConnectionState.ACTIVE

    def invalider(self) -> None:
        self.connection_state = ConnectionState.CLOSED

    def marquer_parole(self) -> None:
        self._verifier_active()
        self.turn_state = TurnState.SPEAKING

    def marquer_silence(self) -> None:
        self._verifier_active()
        self.turn_state = TurnState.SILENT

    def marquer_fin_de_tour(self) -> None:
        self._verifier_active()
        self.turn_state = TurnState.TURN_ENDED

    def signaler_coupure(self) -> None:
        self._verifier_active()
        self.connection_state = ConnectionState.DISCONNECTED

    def entrer_en_reconnexion(self) -> None:
        if self.connection_state == ConnectionState.CLOSED:
            raise SessionFermeeError(f"Session {self.session_id.value} fermée définitivement")
        self.connection_state = ConnectionState.RECONNECTING

    def fermer(self) -> None:
        self.connection_state = ConnectionState.CLOSED

    def est_active(self) -> bool:
        return self.connection_state in (ConnectionState.ACTIVE, ConnectionState.RECONNECTING)

    def _verifier_active(self) -> None:
        if not self.est_active():
            raise SessionNonActiveError(
                f"Session {self.session_id.value} non active (état={self.connection_state.name})"
            )