import os
import asyncpg
from storage.domain.entities.echange import EchangePersiste
from storage.domain.ports.storage_repository_port import StorageRepositoryPort

# Pointer vers le sous-dossier queries/
SQL_FILE_PATH = os.path.join(os.path.dirname(__file__), "queries", "save_exchange.sql")

with open(SQL_FILE_PATH, "r", encoding="utf-8") as f:
    SAVE_EXCHANGE_QUERY = f.read().strip().rstrip(";")


class PostgresStorageRepository(StorageRepositoryPort):
    def __init__(self, db_pool: asyncpg.Pool):
        self._db_pool = db_pool

    async def sauvegarder_dernier_echange(self, echange: EchangePersiste) -> EchangePersiste:
        async with self._db_pool.acquire() as connection:
            row = await connection.fetchrow(
                SAVE_EXCHANGE_QUERY,
                echange.session_id,
                echange.question_agent,
                echange.reponse_candidat,
                echange.qualite_percue,
            )
            if row:
                echange.id = row["id"]
                echange.horodatage = row["horodatage"]
        return echange

    async def mettre_a_jour_statut(self, session_id: str, statut: str) -> None:
        query = """
            UPDATE entretiens
            SET statut = $2
            WHERE session_id = $1;
        """
        async with self._db_pool.acquire() as connection:
            await connection.execute(query, session_id, statut)