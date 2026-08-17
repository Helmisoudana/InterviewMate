from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class AudioChunk:
    data: bytes
    sequence_number: int
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))