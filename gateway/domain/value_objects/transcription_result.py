from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class TranscriptionResult:
    type: Literal["partial", "final"]
    text: str
    confidence: float