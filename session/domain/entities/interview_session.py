from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from shared.domain import SessionID
from session.domain.value_objects.session_config import SessionConfig
from session.domain.value_objects.exchange import Exchange
from session.domain.value_objects.phase import Phase


class InterviewSession:
    def __init__(self, session_id: SessionID, config: SessionConfig) -> None:
        self.session_id = session_id
        self.config = config
        self.phase = Phase.INTRODUCTION
        self.historique: List[Exchange] = []
        self.nombre_questions_posees = 0
        self.derniere_activite = datetime.now(timezone.utc)

    def ajouter_echange(self, question: str, reponse: str) -> None:
        self.historique.append(Exchange(question=question, reponse=reponse))
        self.nombre_questions_posees += 1
        self._toucher()

    def changer_phase(self, phase: Phase) -> None:
        self.phase = phase
        self._toucher()

    def enregistrer_activite(self) -> None:
        self._toucher()

    def est_expiree(self, ttl_secondes: int) -> bool:
        ecoulé = (datetime.now(timezone.utc) - self.derniere_activite).total_seconds()
        return ecoulé > ttl_secondes

    def _toucher(self) -> None:
        self.derniere_activite = datetime.now(timezone.utc)