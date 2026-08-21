from dataclasses import dataclass


@dataclass(frozen=True)
class Evaluation:
    competence: str
    score: float  # 0.0 a 1.0
    justification: str