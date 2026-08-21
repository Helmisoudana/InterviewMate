from dataclasses import dataclass, field
from shared.domain.value_objects import SessionID
from scoring.domain.entities.evaluation import Evaluation


@dataclass
class RapportFinal:
    session_id: SessionID
    score_global: float
    points_forts: list[str] = field(default_factory=list)
    points_faibles: list[str] = field(default_factory=list)
    recommandations: list[str] = field(default_factory=list)
    evaluations: list[Evaluation] = field(default_factory=list)