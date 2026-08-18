from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Exchange:
    question: str
    reponse: str
    horodatage: datetime = field(default_factory=lambda: datetime.now(timezone.utc))