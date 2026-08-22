from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class EchangePersiste:
    session_id: str
    question_agent: str
    reponse_candidat: str
    qualite_percue: Optional[str] = None
    ordre: Optional[int] = None
    entretien_id: Optional[UUID] = None
    id: Optional[int] = None
    horodatage: Optional[datetime] = None