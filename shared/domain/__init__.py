# shared/domain/__init__.py
from .value_objects import (
    SessionID,
    AudioChunk,
    TranscriptionResult,
    InterviewPhase,
    InterviewStage,
    QUESTIONS_PAR_STAGE,
    ORDRE_STAGES,
    stage_to_public_phase,
    Message,
)
from .exceptions import DomainException, SessionNotFoundException, InvalidSessionStateException

__all__ = [
    "SessionID",
    "AudioChunk",
    "TranscriptionResult",
    "InterviewPhase",
    "InterviewStage",
    "QUESTIONS_PAR_STAGE",
    "ORDRE_STAGES",
    "stage_to_public_phase",
    "Message",
    "DomainException",
    "SessionNotFoundException",
    "InvalidSessionStateException",
]