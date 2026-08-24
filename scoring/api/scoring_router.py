from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from dataclasses import asdict
import os
from storage.infrastructure.adapters.postgres_storage_repository import PostgresStorageRepository
from storage.application.use_cases.get_session_transcript import GetSessionTranscriptUseCase
from storage.application.use_cases.get_report import GetReportUseCase
from storage.application.use_cases.save_final_report import SaveFinalReportUseCase
from storage.application.use_cases.update_status import UpdateStatusUseCase

from scoring.infrastructure.adapters.groq_scorer_adapter import GroqScorerAdapter
from scoring.infrastructure.adapters.pdf_rapport_adapter import generer_pdf_rapport
from scoring.application.use_cases.generer_rapport_session import GenererRapportSessionUseCase
from scoring.application.use_cases.generer_pdf import GenererPDF

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PDF_DIR = os.path.join(PARENT_DIR, "pdf")
os.makedirs(PDF_DIR, exist_ok=True)

router = APIRouter(prefix="/scoring")

_storage_repo = PostgresStorageRepository.creer_depuis_env()

GnererRapport = GenererRapportSessionUseCase(
    llm_scorer=GroqScorerAdapter(),
    get_transcript_uc=GetSessionTranscriptUseCase(_storage_repo),
    save_report_uc=SaveFinalReportUseCase(_storage_repo),
    update_status_uc=UpdateStatusUseCase(_storage_repo)

)

GenererPdf=GenererPDF(
    get_report_uc=GetReportUseCase(_storage_repo)

)




@router.get("/{session_id}")
async def obtenir_rapport(session_id: str):
    rapport = await GnererRapport.executer(session_id)
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
    
    
        
    


@router.get("/{session_id}/pdf")
async def obtenir_rapport_pdf(session_id: str):
    try:
        rapport = await GenererPdf.executer(session_id)
        chemin = os.path.join(PDF_DIR, f"rapport_{session_id}.pdf")
        
        generer_pdf_rapport(rapport, chemin)
        
        return FileResponse(
            path=chemin,
            media_type="application/pdf",
            filename=f"rapport_entretien_{session_id}.pdf",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la generation du PDF : {str(e)}"
        )