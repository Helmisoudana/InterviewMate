"""
Point d'entrée LOCAL du module `scoring`.
Lancer avec : python -m scoring.dev_runner
"""

import asyncio
import logging
from unittest.mock import AsyncMock
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scoring.dev_runner")


async def test_avec_fakes():
    logger.info("=== 🧪 TEST MODE FAKE / MOCK ===")

    from scoring.application.use_cases.generer_rapport_session import GenererRapportSessionUseCase

    # 1. Mock du Storage
    mock_storage = AsyncMock()
    mock_storage.recuperer_echanges_par_session.return_value = []

    # 2. Mock du LLM (On mocke EXPLICITEMENT evaluer_transcription avec un retour ASYNCHRONE)
    mock_llm = AsyncMock()
    mock_llm.evaluer_transcription.return_value = {
        "score_global": 16.5,
        "score_technique": 17.0,
        "score_communication": 16.0,
        "points_forts": "Bonne maîtrise des concepts FastAPI et Clean Architecture.",
        "points_faibles": "Un peu synthétique sur l'explication des mocks.",
        "recommandations": "Approfondir la partie gestion des exceptions."
    }

    # 3. Instanciation du Use Case
    use_case = GenererRapportSessionUseCase(
        storage_repo=mock_storage,
        llm_adapter=mock_llm
    )

    # 4. Exécution du Use Case
    session_id_fake = "session-fake-123"
    resultat = await use_case.executer(session_id_fake)

    logger.info("✅ Rapport généré avec succès (Mock) :")
    print("----------------------------------------")
    print(f"Session ID : {resultat.session_id}")
    print(f"Score Global : {resultat.score_global}")
    print(f"Score Technique : {resultat.score_technique}")
    print(f"Score Comms : {resultat.score_communication}")
    print(f"Évaluations ({len(resultat.evaluations)}) : {resultat.evaluations}")
    print("----------------------------------------")


async def main():
    await test_avec_fakes()


if __name__ == "__main__":
    asyncio.run(main())