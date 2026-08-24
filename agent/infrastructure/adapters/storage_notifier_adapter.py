from agent.domain.ports.Storage_notifier_port import StorageNotifierPort
from agent.domain.entities.echange import Echange
from storage.application.use_cases.save_latest_exchange import SaveLatestExchangeUseCase


class StorageNotifierAdapter(StorageNotifierPort):

    def __init__(self, save_latest_exchange_uc: SaveLatestExchangeUseCase):
        self._save_latest_exchange_uc = save_latest_exchange_uc

    async def notifier_echange_termine(self, session_id: str, echange: Echange) -> None:
        question_texte = echange.question or ""
        reponse_texte = echange.reponse or ""
        qualite_percue = "Non evaluee"  

        await self._save_latest_exchange_uc.sauvegarder(
            session_id=session_id,
            question_agent=question_texte,
            reponse_candidat=reponse_texte,
            qualite_percue=qualite_percue,
        )