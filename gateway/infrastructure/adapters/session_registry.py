from dataclasses import dataclass

from gateway.domain.entities.entities import GatewaySession
from shared.domain import SessionID
from gateway.domain.ports.audio_broadcaster_port import AudioBroadcasterPort


@dataclass
class ActiveConnection:
    session: GatewaySession
    broadcaster: AudioBroadcasterPort


class SessionRegistry:
    def __init__(self) -> None:
        self._connections: dict[str, ActiveConnection] = {}

    def enregistrer(self, session_id: SessionID, session: GatewaySession, broadcaster: AudioBroadcasterPort) -> None:
        self._connections[session_id.value] = ActiveConnection(session, broadcaster)

    def obtenir(self, session_id: SessionID) -> ActiveConnection | None:
        return self._connections.get(session_id.value)

    def retirer(self, session_id: SessionID) -> None:
        self._connections.pop(session_id.value, None)