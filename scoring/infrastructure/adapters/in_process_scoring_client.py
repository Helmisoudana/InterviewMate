from shared.domain.value_objects import SessionID, EchangeEvalue
from scoring.application.use_cases.evaluer_echange import EvaluerEchangeUseCase
from scoring.application.use_cases.generer_rapport_final import GenererRapportFinalUseCase
from scoring.domain.entities.rapport_final import RapportFinal


class InProcessScoringClient:
    def __init__(self, evaluer_uc: EvaluerEchangeUseCase, generer_rapport_uc: GenererRapportFinalUseCase):
        self._evaluer = evaluer_uc
        self._generer_rapport = generer_rapport_uc

    async def notifier_echange_termine(self, echange: EchangeEvalue) -> None:
        await self._evaluer.executer(echange)

    async def cloturer_session(self, session_id: SessionID) -> RapportFinal:
        evaluations = self._evaluer.evaluations_pour(session_id)
        return await self._generer_rapport.executer(session_id, evaluations)