import uuid
from datetime import datetime
from typing import Dict, List

from storage.domain.entities.echange import EchangePersiste
from storage.domain.entities.rapport import RapportScorePersiste
from storage.domain.ports.storage_repository_port import StorageRepositoryPort


class FakeStorageRepository(StorageRepositoryPort):
    """Adapter en mémoire, sans Postgres — pour les tests unitaires et le dev_runner hors-ligne."""

    def __init__(self):
        self._echanges: Dict[str, List[EchangePersiste]] = {}
        self._statuts: Dict[str, str] = {}
        self._rapports: Dict[str, RapportScorePersiste] = {}
        self._entretien_ids: Dict[str, str] = {}

    def _entretien_id_pour(self, session_id: str) -> str:
        if session_id not in self._entretien_ids:
            self._entretien_ids[session_id] = str(uuid.uuid4())
        return self._entretien_ids[session_id]

    async def initialiser_entretien(self, session_id: str) -> None:
        self._entretien_id_pour(session_id)
        self._statuts.setdefault(session_id, "EN_COURS")

    async def sauvegarder_dernier_echange(self, echange: EchangePersiste) -> EchangePersiste:
        historique = self._echanges.setdefault(echange.session_id, [])
        echange.id = len(historique) + 1
        echange.entretien_id = self._entretien_id_pour(echange.session_id)
        echange.ordre = len(historique) + 1
        echange.horodatage = datetime.now()
        historique.append(echange)
        self._statuts.setdefault(echange.session_id, "EN_COURS")
        return echange

    async def mettre_a_jour_statut(self, session_id: str, statut: str) -> None:
        self._statuts[session_id] = statut

    async def recuperer_echanges_par_session(self, session_id: str) -> List[EchangePersiste]:
        return list(self._echanges.get(session_id, []))

    async def sauvegarder_rapport(self, rapport: RapportScorePersiste) -> RapportScorePersiste:
        rapport.id = len(self._rapports) + 1
        rapport.entretien_id = self._entretien_id_pour(rapport.session_id)
        rapport.date_creation = datetime.now()
        self._rapports[rapport.session_id] = rapport
        return rapport