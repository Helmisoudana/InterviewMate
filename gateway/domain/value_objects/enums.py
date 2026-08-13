from enum import Enum, auto


class ConnectionState(Enum):
    CONNECTING = auto()
    ACTIVE = auto()
    DISCONNECTED = auto()
    RECONNECTING = auto()
    CLOSED = auto()


class TurnState(Enum):
    SILENT = auto()
    SPEAKING = auto()
    TURN_ENDED = auto()