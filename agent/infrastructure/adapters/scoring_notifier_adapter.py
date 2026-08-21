from agent.domain.ports.scoring_notifier_port import ScoringNotifierPort
from agent.domain.entities.echange import Echange
from shared.domain.value_objects import SessionID, EchangeEvalue, InterviewStage
from scoring.infrastructure.adapters.in_process_scoring_client import InProcessScoringClient


class ScoringNotifierAdapter(ScoringNotifierPort):
    def __init__(self, scoring_client: InProcessScoringClient):
        self._scoring_client = scoring_client

    async def notifier_echange_termine(self, session_id: str, echange: Echange) -> None:
        if echange.reponse is None:
            return  # rien a evaluer si pas encore de reponse

        echange_evalue = EchangeEvalue(
            session_id=SessionID(session_id),
            question=echange.question.texte,
            reponse=echange.reponse.texte,
            phase=InterviewStage(echange.question.phase.value),
        )
        await self._scoring_client.notifier_echange_termine(echange_evalue)