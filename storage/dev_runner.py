import os
import asyncio
import asyncpg
from dotenv import load_dotenv
from storage.infrastructure.adapters.postgres_storage_repository import PostgresStorageRepository
from storage.application.use_cases.save_latest_exchange import SaveLatestExchangeUseCase

# Chargement du fichier .env à la racine
load_dotenv()

async def main():
    # Lecture directe des variables d'environnement
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "interviewmate_db")

    dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    pool = await asyncpg.create_pool(dsn=dsn)
    try:
        repo = PostgresStorageRepository(db_pool=pool)
        use_case = SaveLatestExchangeUseCase(repository=repo)

        resultat = await use_case.sauvegarder(
            session_id="session_dev_test",
            question_agent="Parlez-moi de votre expérience avec Python.",
            reponse_candidat="J'ai développé plusieurs backend en Python.",
            qualite_percue="Excellente"
        )

        print(f"✅ Échange inséré avec succès !")
        print(f" - ID Échange : {resultat.id}")
        print(f" - ID Entretien (UUID) : {resultat.entretien_id}")
        print(f" - Ordre : {resultat.ordre}")

    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(main())