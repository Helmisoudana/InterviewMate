
from dataclasses import dataclass

from domain.entities.models import GatewaySession
from domain.value_objects.session_id import SessionId
from domain.ports.audio_broadcaster_port import AudioBroadcasterPort


@dataclass
class ActiveConnection:
    session: GatewaySession
    broadcaster: AudioBroadcasterPort


class SessionRegistry:
    def __init__(self) -> None:
        self._connections: dict[str, ActiveConnection] = {}

    def enregistrer(self, session_id: SessionId, session: GatewaySession, broadcaster: AudioBroadcasterPort) -> None:
        self._connections[session_id.value] = ActiveConnection(session, broadcaster)

    def obtenir(self, session_id: SessionId) -> ActiveConnection | None:
        return self._connections.get(session_id.value)

    def retirer(self, session_id: SessionId) -> None:
        self._connections.pop(session_id.value, None)