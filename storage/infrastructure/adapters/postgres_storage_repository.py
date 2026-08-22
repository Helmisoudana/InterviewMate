import os
import logging
from typing import List, Optional
import asyncpg
from storage.domain.entities.echange import EchangePersiste
from storage.domain.entities.rapport import RapportScorePersiste
from storage.domain.ports.storage_repository_port import StorageRepositoryPort

logger = logging.getLogger("storage.postgres")

# Pointer vers le sous-dossier queries/
QUERIES_DIR = os.path.join(os.path.dirname(__file__), "queries")


def _charger_requete(nom_fichier: str) -> str:
    chemin = os.path.join(QUERIES_DIR, nom_fichier)
    with open(chemin, "r", encoding="utf-8") as f:
        return f.read().strip().rstrip(";")


SAVE_EXCHANGE_QUERY = _charger_requete("save_exchange.sql")
UPDATE_STATUS_QUERY = _charger_requete("update_status.sql")
GET_ECHANGES_QUERY = _charger_requete("get_echanges_by_session.sql")
SAVE_RAPPORT_QUERY = _charger_requete("save_rapport.sql")


class PostgresStorageRepository(StorageRepositoryPort):
    def __init__(self, db_pool: asyncpg.Pool):
        self._db_pool = db_pool

    @classmethod
    async def creer_depuis_env(cls) -> "PostgresStorageRepository":
        """
        Factory qui construit le pool Postgres a partir des variables d'environnement
        (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD) et retourne le repository pret a l'emploi.

        Toute la logique de connexion (dsn, asyncpg.create_pool) reste dans le module storage :
        gateway/server.py n'a plus besoin d'importer asyncpg ni de connaitre la DSN.
        """
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "interviewmate_db")

        dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        logger.info("Connexion à PostgreSQL sur %s:%s...", host, port)
        pool = await asyncpg.create_pool(dsn=dsn)
        return cls(db_pool=pool)

    async def fermer(self) -> None:
        """Ferme le pool de connexions. A appeler explicitement au shutdown de l'application."""
        if self._db_pool:
            await self._db_pool.close()

    async def sauvegarder_dernier_echange(self, echange: EchangePersiste) -> EchangePersiste:
        async with self._db_pool.acquire() as connection:
            row = await connection.fetchrow(
                SAVE_EXCHANGE_QUERY,
                str(echange.session_id),
                echange.question_agent,
                echange.reponse_candidat,
                echange.qualite_percue,
            )
            if row:
                # BUG corrigé : entretien_id et ordre n'étaient jamais réassignés
                # alors que la requête SQL les retournait déjà (RETURNING id, entretien_id, ordre, horodatage)
                echange.id = row["id"]
                echange.entretien_id = row["entretien_id"]
                echange.ordre = row["ordre"]
                echange.horodatage = row["horodatage"]
        return echange

    async def mettre_a_jour_statut(self, session_id: str, statut: str) -> None:
        # asyncpg exige un str pur ; certains appelants (ex. close_session.py côté gateway)
        # passent l'objet SessionID directement. SessionID.__str__ renvoie déjà .value.
        async with self._db_pool.acquire() as connection:
            await connection.execute(UPDATE_STATUS_QUERY, str(session_id), statut)

    async def recuperer_echanges_par_session(self, session_id: str) -> List[EchangePersiste]:
        """Récupère tous les échanges d'un entretien, ordonnés par 'ordre', pour le futur module scoring."""
        async with self._db_pool.acquire() as connection:
            rows = await connection.fetch(GET_ECHANGES_QUERY, str(session_id))
        return [
            EchangePersiste(
                id=row["id"],
                entretien_id=row["entretien_id"],
                ordre=row["ordre"],
                session_id=str(session_id),
                question_agent=row["question_agent"],
                reponse_candidat=row["reponse_candidat"],
                qualite_percue=row["qualite_percue"],
                horodatage=row["horodatage"],
            )
            for row in rows
        ]

    async def sauvegarder_rapport(self, rapport: RapportScorePersiste) -> RapportScorePersiste:
        """Persiste le rapport final de scoring (table rapports_scoring) pour un entretien."""
        async with self._db_pool.acquire() as connection:
            row = await connection.fetchrow(
                SAVE_RAPPORT_QUERY,
                rapport.session_id,
                rapport.score_global,
                rapport.score_technique,
                rapport.score_communication,
                rapport.points_forts,
                rapport.points_faibles,
                rapport.recommandations,
            )
            if row:
                rapport.id = row["id"]
                rapport.entretien_id = row["entretien_id"]
                rapport.date_creation = row["date_creation"]
        return rapport