from shared.domain.value_objects import SessionID
from scoring.domain.entities.rapport_final import RapportFinal
from scoring.domain.entities.evaluation import Evaluation
from scoring.domain.ports.storage_client_port import StorageClientPort


class GenererRapportFinalUseCase:
    def __init__(self, storage_client: StorageClientPort):
        self._storage_client = storage_client

    async def executer(self, session_id: SessionID, evaluations: list[Evaluation]) -> RapportFinal:
        score_global = sum(e.score for e in evaluations) / len(evaluations) if evaluations else 0.0
        rapport = RapportFinal(
            session_id=session_id,
            score_global=score_global,
            evaluations=evaluations,
        )
        await self._storage_client.sauvegarder_rapport(rapport)
        return rapport