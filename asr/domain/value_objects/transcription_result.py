from dataclasses import dataclass
from typing import Literal

TranscriptionType = Literal["partial", "final"]


@dataclass(frozen=True)
class TranscriptionResult:
    type: TranscriptionType
    text: str
    confidence: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence doit être entre 0 et 1")