# shared/domain/value_objects.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import uuid


@dataclass(frozen=True)
class SessionID:
    """Identifiant unique de session partagé entre tous les modules."""
    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("SessionID doit être une chaîne non vide.")

    @classmethod
    def generate(classmethod) -> "SessionID":
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AudioChunk:
    """Bloc audio transmis par le Gateway vers ASR."""
    session_id: SessionID
    data: bytes
    sample_rate: int = 16000
    is_final: bool = False

    def __post_init__(self):
        if not isinstance(self.data, bytes):
            raise ValueError("Le paramètre data doit être de type bytes.")


@dataclass(frozen=True)
class TranscriptionResult:
    """Résultat de la transcription transmis par ASR vers Gateway/Agent."""
    session_id: SessionID
    text: str
    is_final: bool
    confidence: float = 1.0


class InterviewPhase(str, Enum):
    """Phases standard d'un entretien."""
    INIT = "INIT"
    INTRO = "INTRO"
    QUESTIONNING = "QUESTIONNING"
    CONCLUSION = "CONCLUSION"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class Message:
    """Message échangé dans le cadre de l'entretien (User ou Assistant)."""
    role: str  # "user" ou "assistant" ou "system"
    content: str
    timestamp: float