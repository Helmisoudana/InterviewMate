# shared/contracts/dtos.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from shared.domain.value_objects import SessionID, InterviewPhase


@dataclass(frozen=True)
class StartSessionRequestDTO:
    user_id: str
    candidate_name: str
    job_title: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StartSessionResponseDTO:
    session_id: SessionID
    status: str
    initial_prompt_audio: Optional[bytes] = None


@dataclass(frozen=True)
class VoiceResponseRequestDTO:
    session_id: SessionID
    user_text: str


@dataclass(frozen=True)
class VoiceResponseDTO:
    session_id: SessionID
    text_response: str
    audio_data: Optional[bytes] = None
    phase: InterviewPhase = InterviewPhase.QUESTIONNING


@dataclass(frozen=True)
class SessionStateDTO:
    session_id: SessionID
    phase: InterviewPhase
    history: List[Dict[str, str]] = field(default_factory=list)
    is_active: bool = True