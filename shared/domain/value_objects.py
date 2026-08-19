# shared/domain/value_objects.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import time
import uuid


@dataclass(frozen=True)
class SessionID:
    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("SessionID doit être une chaîne non vide.")

    @classmethod
    def generate(cls) -> "SessionID":
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AudioChunk:
    session_id: SessionID
    data: bytes
    sample_rate: int = 16000
    is_final: bool = False
    sequence_number: Optional[int] = None
    captured_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not isinstance(self.data, bytes):
            raise ValueError("Le paramètre data doit être de type bytes.")


@dataclass(frozen=True)
class TranscriptionResult:
    session_id: SessionID
    text: str
    is_final: bool
    confidence: float = 1.0


class InterviewPhase(str, Enum):

    INIT = "INIT"
    INTRO = "INTRO"
    QUESTIONNING = "QUESTIONNING"
    CONCLUSION = "CONCLUSION"
    CLOSED = "CLOSED"


class InterviewStage(str, Enum):

    INTRO = "intro"
    TECHNIQUE = "technique"
    COMPORTEMENTAL = "comportemental"
    CLOTURE = "cloture"
    TERMINEE = "terminee"


QUESTIONS_PAR_STAGE = {
    InterviewStage.INTRO: 1,
    InterviewStage.TECHNIQUE: 4,
    InterviewStage.COMPORTEMENTAL: 2,
    InterviewStage.CLOTURE: 1,
}

ORDRE_STAGES = [
    InterviewStage.INTRO,
    InterviewStage.TECHNIQUE,
    InterviewStage.COMPORTEMENTAL,
    InterviewStage.CLOTURE,
]

_STAGE_TO_PUBLIC_PHASE = {
    InterviewStage.INTRO: InterviewPhase.INTRO,
    InterviewStage.TECHNIQUE: InterviewPhase.QUESTIONNING,
    InterviewStage.COMPORTEMENTAL: InterviewPhase.QUESTIONNING,
    InterviewStage.CLOTURE: InterviewPhase.CONCLUSION,
    InterviewStage.TERMINEE: InterviewPhase.CLOSED,
}


def stage_to_public_phase(stage: "InterviewStage") -> "InterviewPhase":

    return _STAGE_TO_PUBLIC_PHASE.get(stage, InterviewPhase.INTRO)


@dataclass(frozen=True)
class Message:
    role: str  
    content: str
    timestamp: float = field(default_factory=time.time)