from dataclasses import dataclass, field
from typing import Optional, List
@dataclass
class EvaluationEchange:
    ordre: int
    question: str
    reponse: str
    qualite_percue: str
    score_technique: float
    remarque: str = ""
@dataclass
class RapportScore:
    session_id: str
    score_global: float
    points_forts: List[str] = field(default_factory=list)
    points_faibles: List[str] = field(default_factory=list)
    recommandations: List[str] = field(default_factory=list)
    evaluations: List[EvaluationEchange] = field(default_factory=list)
    score_technique: Optional[float] = None
    score_communication: Optional[float] = None