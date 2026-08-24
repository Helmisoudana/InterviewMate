import asyncio

from storage.infrastructure.adapters.postgres_storage_repository import PostgresStorageRepository
from storage.application.use_cases.get_session_transcript import GetSessionTranscriptUseCase
from storage.application.use_cases.get_report import GetReportUseCase
from storage.application.use_cases.save_final_report import SaveFinalReportUseCase

from scoring.infrastructure.fakes.fake_llm_scorer_adapter import FakeLLMScorerAdapter
from scoring.application.use_cases.generer_rapport_session import GenererRapportSessionUseCase


async def main():
    storage_repo = PostgresStorageRepository.creer_depuis_env()
    try:
        use_case = GenererRapportSessionUseCase(
            llm_scorer=FakeLLMScorerAdapter(),  # remplace par GroqScorerAdapter() pour le vrai appel
            get_transcript_uc=GetSessionTranscriptUseCase(storage_repo),
            get_report_uc=GetReportUseCase(storage_repo),
            save_report_uc=SaveFinalReportUseCase(storage_repo),
        )

        session_id = "session_dev_test"  # une session deja peuplee via storage.dev_runner
        rapport = await use_case.executer(session_id)

        print(f"✅ Rapport pour {session_id}")
        print(f" - Score global : {rapport.score_global}")
        print(f" - Points forts : {rapport.points_forts}")
        print(f" - Points faibles : {rapport.points_faibles}")
        print(f" - Nb evaluations : {len(rapport.evaluations)}")
    finally:
        await storage_repo.fermer()


if __name__ == "__main__":
    asyncio.run(main())