from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class RapportScorePersiste:
    """
    Représente le rapport final de scoring d'un entretien,
    tel que persisté dans la table 'rapports_scoring'.
    Rempli par le module 'scoring' après son unique appel LLM
    à la clôture de la session.
    """
    session_id: str
    score_global: float
    points_forts: List[str] = field(default_factory=list)
    points_faibles: List[str] = field(default_factory=list)
    recommandations: List[str] = field(default_factory=list)
    score_technique: Optional[float] = None
    score_communication: Optional[float] = None
    id: Optional[int] = None
    entretien_id: Optional[str] = None
    date_creation: Optional[datetime] = None
