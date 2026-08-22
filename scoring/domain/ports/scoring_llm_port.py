from abc import ABC, abstractmethod
from typing import Dict, Any


class ScoringLLMPort(ABC):
    @abstractmethod
    async def evaluer_transcription(self, transcription: str) -> Dict[str, Any]:
        """Analyse le texte complet de l'entretien et retourne un dictionnaire de notes et commentaires."""
        pass