from fastapi import APIRouter, HTTPException
from dataclasses import asdict

from storage.infrastructure.adapters.postgres_storage_repository import PostgresStorageRepository
from storage.application.use_cases.get_session_transcript import GetSessionTranscriptUseCase
from storage.application.use_cases.get_report import GetReportUseCase
from storage.application.use_cases.save_final_report import SaveFinalReportUseCase

from scoring.infrastructure.adapters.groq_scorer_adapter import GroqScorerAdapter
from scoring.application.use_cases.generer_rapport_session import GenererRapportSessionUseCase

router = APIRouter(prefix="/scoring")

# Meme repository que storage/api/api.py (creer_depuis_env est synchrone, pool paresseux au premier appel)
_storage_repo = PostgresStorageRepository.creer_depuis_env()

_use_case = GenererRapportSessionUseCase(
    llm_scorer=GroqScorerAdapter(),
    get_transcript_uc=GetSessionTranscriptUseCase(_storage_repo),
    get_report_uc=GetReportUseCase(_storage_repo),
    save_report_uc=SaveFinalReportUseCase(_storage_repo),
)


@router.get("/{session_id}")
async def obtenir_rapport(session_id: str):
    """
    Appele par le bouton 'Rapport' du frontend.
    Pattern get-or-generate : si le rapport existe deja en base, retour instantane
    (aucun nouvel appel Groq). Sinon, il est genere a la demande, sauvegarde, puis retourne.
    """
    try:
        rapport = await _use_case.executer(session_id)
        return {
            "session_id": rapport.session_id,
            "score_global": rapport.score_global,
            "score_technique": rapport.score_technique,
            "score_communication": rapport.score_communication,
            "points_forts": rapport.points_forts,
            "points_faibles": rapport.points_faibles,
            "recommandations": rapport.recommandations,
            "evaluations": [asdict(ev) for ev in rapport.evaluations],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la generation du rapport : {str(e)}"
        )