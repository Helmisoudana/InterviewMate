from agent.domain.ports.scoring_notifier_port import ScoringNotifierPort
from agent.domain.entities.echange import Echange
from storage.application.use_cases.save_latest_exchange import SaveLatestExchangeUseCase


class StorageNotifierAdapter(ScoringNotifierPort):
    """Adaptateur reliant le port de notification de l'agent au Use Case de persistance Storage."""

    def __init__(self, save_latest_exchange_uc: SaveLatestExchangeUseCase):
        self._save_latest_exchange_uc = save_latest_exchange_uc

    async def notifier_echange_termine(self, session_id: str, echange: Echange) -> None:
        question_texte = echange.question.texte if echange.question else ""
        reponse_texte = echange.reponse.texte if echange.reponse else ""
        qualite_percue = echange.reponse.qualite_percue if echange.reponse else "Non évaluée"

        await self._save_latest_exchange_uc.sauvegarder(
            session_id=session_id,
            question_agent=question_texte,
            reponse_candidat=reponse_texte,
            qualite_percue=qualite_percue,
        )