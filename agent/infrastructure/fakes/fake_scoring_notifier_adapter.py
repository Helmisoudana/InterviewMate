from agent.domain.ports.scoring_notifier_port import ScoringNotifierPort
from agent.domain.entities.interview import Echange


class FakeScoringNotifierAdapter(ScoringNotifierPort):
    async def notifier_echange_termine(self, session_id: str, echange: Echange) -> None:
        print(f"[FAKE SCORING] echange notifie pour la session {session_id} : {echange.question.texte}")