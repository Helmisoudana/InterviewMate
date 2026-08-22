from fastapi import APIRouter, HTTPException
from scoring.application.use_cases.generer_rapport_session import GenererRapportSessionUseCase

router = APIRouter(prefix="/scoring", tags=["Scoring"])

_generer_rapport_uc: GenererRapportSessionUseCase = None


def initialiser_scoring_router(use_case: GenererRapportSessionUseCase):
    global _generer_rapport_uc
    _generer_rapport_uc = use_case


@router.post("/evaluer/{session_id}")
async def evaluer_session(session_id: str):
    if not _generer_rapport_uc:
        raise HTTPException(
            status_code=500, detail="Le service de Scoring n'est pas initialisé."
        )
    try:
        rapport = await _generer_rapport_uc.executer(session_id)
        return {
            "status": "success",
            "session_id": session_id,
            "rapport": rapport,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))