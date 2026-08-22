from dataclasses import dataclass, field
from typing import List


@dataclass
class EvaluationDetail:
    critere: str
    note: float
    commentaire: str


@dataclass
class RapportScore:
    session_id: str
    score_global: float
    score_technique: float
    score_communication: float
    points_forts: str
    points_faibles: str
    recommandations: str
    evaluations: List[EvaluationDetail] = field(default_factory=list)