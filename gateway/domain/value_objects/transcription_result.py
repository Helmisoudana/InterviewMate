from dataclasses import dataclass
from typing import Literal

TranscriptionType = Literal["partial", "final"]


@dataclass(frozen=True)
class TranscriptionResult:
    type: TranscriptionType
    text: str
    confidence: float