from scoring.domain.ports.storage_client_port import StorageClientPort
from scoring.domain.entities.rapport_final import RapportFinal


class FakeStorageClientAdapter(StorageClientPort):
    async def sauvegarder_rapport(self, rapport: RapportFinal) -> None:
        print(f"[FAKE STORAGE] rapport sauvegarde pour {rapport.session_id} : score={rapport.score_global}")